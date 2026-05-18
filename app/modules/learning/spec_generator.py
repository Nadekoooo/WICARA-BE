from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.language import normalize_language_code
from app.modules.ai import ai_client
from app.modules.ai.config import DEFAULT_AI_MODEL
from app.modules.ai.errors import AIConfigurationError, AIError
from app.modules.ai.schemas import AIGenerationResponse
from app.modules.learning.concept_template_router import (
    resolve_primary_template_id,
    resolve_template_candidates,
)
from app.modules.learning.template_registry import (
    TemplateRegistryError,
    registered_template_ids,
    resolve_template_entry,
)
from app.modules.learning.template_quality import evaluate_template_quality
from app.modules.learning.template_validation import (
    TemplateValidationError,
    validate_template_spec,
)
from app.modules.workspaces.models import WorkspaceEvent, WorkspaceSession

_PROMPT_VERSION = "workspace_context_spec_openrouter_v1"
_ROUTER_PROMPT_VERSION = "workspace_context_template_router_openrouter_v1"
_DEFAULT_MODEL = DEFAULT_AI_MODEL
_MAX_ATTEMPTS = 2
_SPEC_MAX_OUTPUT_TOKENS = 8192
_PREVIOUS_RESPONSE_FEEDBACK_LIMIT = 1800
_ROOT_DIR = Path(__file__).resolve().parents[3]
_SAMPLE_SPECS_DIR = _ROOT_DIR / "wicara_mvp_10_manim_templates" / "specs" / "samples"

_SYSTEM_INSTRUCTION = """
You are a backend spec generator for educational video templates (Manim or Remotion).
Task:
- Produce exactly one JSON object that follows the requested template schema.
- Adapt content to the latest workspace conversation context.
- Keep the tone instructional and concise for students.

Hard requirements:
- Return JSON only, no markdown, no explanation.
- Keep `template_id` exactly as requested.
- Use `language` exactly as requested in `requested_language`.
- Keep all textual fields (title, subtitle, steps, narration) in that same language.
- Include narration fields so voiceover can be generated cleanly.
- Keep values realistic and classroom-safe.
- Keep narration pacing balanced: avoid long intro and provide clear narration per step.
""".strip()

_ROUTER_SYSTEM_INSTRUCTION = """
You are a backend template router for educational video templates (Manim or Remotion).
Task:
- Choose exactly one template_id from allowed_template_ids.
- Use the workspace context and concept_type signal.

Hard requirements:
- Return JSON only, no markdown.
- Use exact format: {"template_id":"...","reason":"..."}.
- template_id must be one value from allowed_template_ids.
- Prefer templates whose semantic domain matches learner context.
""".strip()


class WorkspaceContextSpecGenerationError(ValueError):
    pass


@dataclass(frozen=True)
class WorkspaceGeneratedSpec:
    template_id: str
    spec_json: dict[str, Any]
    debug_meta: dict[str, Any]


def generate_spec_from_workspace_context(
    *,
    workspace: WorkspaceSession,
    language: str,
) -> WorkspaceGeneratedSpec:
    metadata = dict(workspace.metadata_json or {})
    active_concept_type = str(metadata.get("active_concept_type") or "").strip().lower()
    raw_template_id = str(metadata.get("active_template_id") or "").strip().lower()
    template_resolution_source = "active_template_id"
    router_candidates = resolve_template_candidates(active_concept_type)
    mapped_template_id = resolve_primary_template_id(active_concept_type)
    if not router_candidates and mapped_template_id:
        router_candidates = [mapped_template_id]
    router_used = False
    requested_language = _normalize_language(language)
    context_snapshot = _build_context_snapshot(
        workspace=workspace,
        metadata=metadata,
        requested_language=requested_language,
    )

    if raw_template_id and router_candidates:
        normalized_candidates = {
            str(candidate).strip().lower()
            for candidate in router_candidates
            if str(candidate).strip()
        }
        if raw_template_id not in normalized_candidates:
            raw_template_id = mapped_template_id or router_candidates[0]
            template_resolution_source = "concept_type_route_overrode_active_template_id"

    if not raw_template_id:
        if router_candidates:
            planned = _select_template_id_with_ai(
                concept_type=active_concept_type,
                requested_language=requested_language,
                context_snapshot=context_snapshot,
                allowed_template_ids=router_candidates,
            )
            if planned:
                raw_template_id = planned
                template_resolution_source = "openrouter_router_candidates"
                router_used = True
            else:
                raw_template_id = router_candidates[0]
                template_resolution_source = "concept_type_candidates_fallback"
        elif mapped_template_id:
            raw_template_id = mapped_template_id
            template_resolution_source = "concept_type_route_primary"
        else:
            global_candidates = _global_router_candidates()
            router_candidates = global_candidates
            planned = _select_template_id_with_ai(
                concept_type=active_concept_type,
                requested_language=requested_language,
                context_snapshot=context_snapshot,
                allowed_template_ids=global_candidates,
            )
            if planned:
                raw_template_id = planned
                template_resolution_source = "openrouter_router_global"
                router_used = True

    if not raw_template_id:
        raise WorkspaceContextSpecGenerationError(
            "Workspace context is missing active_template_id and no template route could be resolved."
        )

    try:
        resolved = resolve_template_entry(raw_template_id)
    except TemplateRegistryError as exc:
        raise WorkspaceContextSpecGenerationError(str(exc)) from exc

    template_id = resolved.entry.template_id
    node_id = str(metadata.get("active_node_id") or "").strip()
    sample_spec = _load_sample_spec(template_id)

    last_error: str | None = None
    last_response: str | None = None
    validation_details: list[dict[str, Any]] = []
    final_ai_response: AIGenerationResponse | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        user_instruction = _build_user_instruction(
            template_id=template_id,
            requested_language=requested_language,
            workspace_id=str(workspace.id),
            context_snapshot=context_snapshot,
            sample_spec=sample_spec,
            previous_error=last_error,
            validation_details=validation_details,
            previous_response=last_response,
        )
        ai_response = _generate_with_ai(user_instruction=user_instruction)
        final_ai_response = ai_response
        try:
            candidate_payload = _parse_candidate_spec(ai_response.text)
        except WorkspaceContextSpecGenerationError as exc:
            last_error = str(exc)
            validation_details = [
                {
                    "path": "response",
                    "message": str(exc),
                    "type": "json_parse_error",
                    "finish_reason": ai_response.finish_reason,
                }
            ]
            last_response = _feedback_response_excerpt(ai_response.text)
            if attempt >= _MAX_ATTEMPTS:
                raise
            continue
        candidate_payload["template_id"] = template_id
        candidate_payload["language"] = requested_language
        candidate_payload.setdefault("id", f"context_auto_{workspace.id}")
        if node_id:
            candidate_payload.setdefault("node_id", node_id)

        try:
            validation_result = validate_template_spec(
                template_id=template_id,
                spec_json=candidate_payload,
            )
        except TemplateValidationError as exc:
            last_error = exc.message
            validation_details = exc.details
            last_response = _feedback_response_excerpt(ai_response.text)
            if attempt >= _MAX_ATTEMPTS:
                raise WorkspaceContextSpecGenerationError(
                    f"AI generated an invalid spec for {template_id}: {exc.message}"
                ) from exc
            continue

        quality_result = evaluate_template_quality(
            template_id=template_id,
            spec_json=validation_result.normalized_spec,
        )
        if not quality_result.passed:
            quality_errors = [issue.message for issue in quality_result.errors]
            last_error = "Template quality lint failed."
            validation_details = quality_result.to_feedback_details()
            last_response = _feedback_response_excerpt(ai_response.text)
            if attempt >= _MAX_ATTEMPTS:
                error_text = "; ".join(quality_errors) if quality_errors else "Unknown quality issue."
                raise WorkspaceContextSpecGenerationError(
                    f"AI generated low-quality pacing for {template_id}: {error_text}"
                )
            continue

        debug_meta: dict[str, Any] = {
            "spec_source": "context_auto_backend_openrouter",
            "prompt_version": _PROMPT_VERSION,
            "resolved_template_id": template_id,
            "template_resolution_source": template_resolution_source,
            "resolved_node_id": node_id or None,
            "resolved_concept_type": active_concept_type or None,
            "resolved_prerequisites": metadata.get("active_prerequisites"),
            "context_source": metadata.get("context_source"),
            "language": requested_language,
            "requested_language": requested_language,
            "router_used": router_used,
            "router_prompt_version": _ROUTER_PROMPT_VERSION if router_used else None,
            "router_candidate_count": len(router_candidates),
            "router_candidates": router_candidates[:20],
            "attempt": attempt,
            "ai_source": ai_response.provider,
            "ai_model": ai_response.model,
            "ai_finish_reason": ai_response.finish_reason,
            "input_tokens": ai_response.usage.input_tokens if ai_response.usage else None,
            "output_tokens": ai_response.usage.output_tokens if ai_response.usage else None,
            "conversation_turns_used": len(context_snapshot["recent_turns"]),
            "quality_lint": {
                "passed": quality_result.passed,
                "details": quality_result.to_feedback_details()[:8],
                "error_count": len(quality_result.errors),
                "warning_count": len(quality_result.warnings),
                "metrics": quality_result.metrics,
            },
        }
        return WorkspaceGeneratedSpec(
            template_id=template_id,
            spec_json=validation_result.normalized_spec,
            debug_meta=debug_meta,
        )

    raise WorkspaceContextSpecGenerationError(
        "AI spec generation failed unexpectedly."
    )


def _normalize_language(language: str) -> str:
    return normalize_language_code(language)[:16]


def _load_sample_spec(template_id: str) -> dict[str, Any]:
    sample_path = _SAMPLE_SPECS_DIR / template_id / "sample_01.json"
    if not sample_path.exists():
        raise WorkspaceContextSpecGenerationError(
            f"Sample spec not found for template '{template_id}' at {sample_path}."
        )
    try:
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkspaceContextSpecGenerationError(
            f"Failed to load sample spec for '{template_id}': {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise WorkspaceContextSpecGenerationError(
            f"Sample spec for '{template_id}' must be a JSON object."
        )
    return payload


def _build_context_snapshot(
    *,
    workspace: WorkspaceSession,
    metadata: dict[str, Any],
    requested_language: str,
) -> dict[str, Any]:
    recent_turns = _recent_turns(workspace.events or [], max_turns=8)
    latest_learner_text = ""
    for turn in reversed(recent_turns):
        if turn["role"] == "learner":
            latest_learner_text = turn["text"]
            break

    return {
        "workspace_id": str(workspace.id),
        "current_topic": (workspace.current_topic or "").strip(),
        "requested_language": requested_language,
        "active_node_id": _jsonable(metadata.get("active_node_id")),
        "active_concept_type": _jsonable(metadata.get("active_concept_type")),
        "active_template_id": _jsonable(metadata.get("active_template_id")),
        "active_prerequisites": _jsonable(metadata.get("active_prerequisites")),
        "context_source": _jsonable(metadata.get("context_source")),
        "latest_learner_text": latest_learner_text,
        "recent_turns": recent_turns,
    }


def _recent_turns(events: list[WorkspaceEvent], *, max_turns: int) -> list[dict[str, str]]:
    lines: list[dict[str, str]] = []
    for event in events[-(max_turns * 2) :]:
        text = str(event.text_payload or "").strip()
        if not text:
            continue
        actor = str(event.actor_type or "").strip().lower()
        role = "learner" if actor == "learner" else "assistant"
        lines.append({"role": role, "text": text})
    return lines[-max_turns:]


def _global_router_candidates() -> list[str]:
    try:
        rows = registered_template_ids()
    except TemplateRegistryError:
        return []
    return sorted(set(rows))


def _select_template_id_with_ai(
    *,
    concept_type: str,
    requested_language: str,
    context_snapshot: dict[str, Any],
    allowed_template_ids: list[str],
) -> str | None:
    normalized_candidates = [str(item).strip().lower() for item in allowed_template_ids if str(item).strip()]
    normalized_candidates = sorted(set(normalized_candidates))
    if not normalized_candidates:
        return None

    instruction_payload = {
        "task": "choose_template_id",
        "requested_language": requested_language or "en",
        "active_concept_type": concept_type or "",
        "allowed_template_ids": normalized_candidates,
        "workspace_context": {
            "current_topic": context_snapshot.get("current_topic"),
            "latest_learner_text": context_snapshot.get("latest_learner_text"),
            "recent_turns": context_snapshot.get("recent_turns", []),
            "active_prerequisites": context_snapshot.get("active_prerequisites"),
        },
        "output_contract": {
            "json_only": True,
            "must_use_allowed_template_id": True,
            "format": {"template_id": "string", "reason": "string"},
        },
    }
    user_instruction = json.dumps(instruction_payload, ensure_ascii=True, indent=2)
    params = {
        "temperature": 0.1,
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
    }

    try:
        response = _run_async_generate(
            system_instruction=_ROUTER_SYSTEM_INSTRUCTION,
            user_instruction=user_instruction,
            params=params,
        )
    except (AIConfigurationError, AIError):
        return None

    payload = _try_parse_json_object_response(response.text)
    if payload is None:
        return None

    selected = str(payload.get("template_id") or "").strip().lower()
    if not selected:
        return None
    if selected not in normalized_candidates:
        return None
    return selected


def _build_user_instruction(
    *,
    template_id: str,
    requested_language: str,
    workspace_id: str,
    context_snapshot: dict[str, Any],
    sample_spec: dict[str, Any],
    previous_error: str | None,
    validation_details: list[dict[str, Any]],
    previous_response: str | None,
) -> str:
    base_payload: dict[str, Any] = {
        "task": "generate_template_spec_json",
        "template_id": template_id,
        "requested_language": requested_language or "en",
        "output_contract": {
            "must_return_json_object": True,
            "must_include_language_field": True,
            "must_match_text_language_with_language_field": True,
            "must_use_requested_language_exactly": True,
        },
        "workspace_id": workspace_id,
        "instructions": [
            "Use the sample spec structure as reference.",
            "Adapt the content to the context conversation.",
            "Use requested_language exactly for all user-facing text.",
            "Do not switch language, mix languages, or auto-detect another language.",
            "Keep required fields complete.",
            "Keep narration fields coherent with steps.",
            "Provide at least 2 instructional steps with narration on each step.",
            "Distribute explanation to step narration, not only intro.",
            "Do not return markdown.",
        ],
        "context_snapshot": context_snapshot,
        "sample_spec_reference": sample_spec,
    }
    if previous_error:
        base_payload["retry_feedback"] = {
            "previous_error": previous_error,
            "validation_details": validation_details,
            "previous_response": previous_response,
        }
    return json.dumps(base_payload, ensure_ascii=True, indent=2)


def _generate_with_ai(*, user_instruction: str) -> AIGenerationResponse:
    params = {
        "temperature": 0.3,
        "max_tokens": _SPEC_MAX_OUTPUT_TOKENS,
        "response_format": {"type": "json_object"},
    }
    try:
        return _run_async_generate(
            system_instruction=_SYSTEM_INSTRUCTION,
            user_instruction=user_instruction,
            params=params,
        )
    except AIConfigurationError as exc:
        raise WorkspaceContextSpecGenerationError(str(exc)) from exc
    except AIError as exc:
        raise WorkspaceContextSpecGenerationError(
            f"AI spec generation failed: {exc}"
        ) from exc


def _run_async_generate(
    *,
    system_instruction: str,
    user_instruction: str,
    params: dict[str, Any],
) -> AIGenerationResponse:
    async def _call() -> AIGenerationResponse:
        return await ai_client.generate(
            provider="openrouter",
            model=_DEFAULT_MODEL,
            system_instruction=system_instruction,
            user_instruction=user_instruction,
            params=params,
        )

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_call())

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(lambda: asyncio.run(_call())).result()


def _parse_candidate_spec(raw_text: str) -> dict[str, Any]:
    payload = _try_parse_json_object_response(raw_text)
    if payload is None:
        raise WorkspaceContextSpecGenerationError(
            "AI response is not a valid JSON object for spec generation."
        )
    return payload


def _try_parse_json_object_response(raw_text: str) -> dict[str, Any] | None:
    text = (raw_text or "").strip()
    if not text:
        return None

    candidates = [text]
    fenced = _extract_fenced_json(text)
    if fenced:
        candidates.append(fenced)
    sliced = _slice_outer_object(text)
    if sliced and sliced not in candidates:
        candidates.append(sliced)

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _feedback_response_excerpt(raw_text: str) -> str:
    text = (raw_text or "").strip()
    if len(text) <= _PREVIOUS_RESPONSE_FEEDBACK_LIMIT:
        return text
    return f"{text[:_PREVIOUS_RESPONSE_FEEDBACK_LIMIT]}...[truncated]"


def _extract_fenced_json(text: str) -> str:
    marker = "```"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find(marker, start + len(marker))
    if end < 0:
        return ""
    chunk = text[start + len(marker) : end].strip()
    if chunk.lower().startswith("json"):
        chunk = chunk[4:].strip()
    return chunk


def _slice_outer_object(text: str) -> str:
    left = text.find("{")
    right = text.rfind("}")
    if left < 0 or right < 0 or right <= left:
        return ""
    return text[left : right + 1]


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return str(value)
