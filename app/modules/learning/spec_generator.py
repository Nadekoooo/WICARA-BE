from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.modules.workspaces.models import WorkspaceSession

_PILOT_NODE_ID = "km_d_matematika_bilangan_bulat"
_PILOT_CONCEPT_TYPE = "number_line_quantity_model"
_PILOT_TEMPLATE_ID = "manim.number_line_quantity.v1"
_PILOT_PREREQUISITES = ["km_c_matematika_bilangan_cacah_sampai_1000000"]


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
    concept_type = str(metadata.get("active_concept_type") or "").strip().lower()
    template_id = str(metadata.get("active_template_id") or "").strip().lower()
    node_id = str(metadata.get("active_node_id") or "").strip()

    if not concept_type:
        raise WorkspaceContextSpecGenerationError(
            "Workspace context is missing active_concept_type."
        )
    if not template_id:
        raise WorkspaceContextSpecGenerationError(
            "Workspace context is missing active_template_id."
        )
    if concept_type != _PILOT_CONCEPT_TYPE or template_id != _PILOT_TEMPLATE_ID:
        raise WorkspaceContextSpecGenerationError(
            "Only the number-line pilot context is supported for context_auto mode."
        )

    normalized_language = _normalize_language(language)
    is_id = normalized_language == "id"
    learner_focus_text = _latest_learner_focus_text(workspace)

    title = (workspace.current_topic or "").strip()
    if not title:
        title = (
            "Bilangan pada Garis Bilangan"
            if is_id
            else "Numbers on the Number Line"
        )

    subtitle = (
        "Semakin ke kanan, nilainya semakin besar."
        if is_id
        else "Values get larger as we move to the right."
    )
    if learner_focus_text:
        subtitle = (
            f"Fokus diskusi: {learner_focus_text[:90]}"
            if is_id
            else f"Discussion focus: {learner_focus_text[:90]}"
        )
    intro = (
        "Perhatikan garis bilangan ini. Angka negatif di kiri dan angka positif di kanan."
        if is_id
        else "Look at this number line. Negative numbers are on the left and positive numbers are on the right."
    )
    step_1_narration = (
        "Lihat posisi angkanya. Minus dua ada di kiri, sedangkan tiga ada di kanan."
        if is_id
        else "Observe the positions. Negative two is on the left, while three is on the right."
    )
    step_2_narration = (
        "Bandingkan nilainya. Angka yang lebih kanan pada garis bilangan nilainya lebih besar."
        if is_id
        else "Now compare values. The number farther to the right is greater on a number line."
    )
    summary = (
        "Pada garis bilangan, angka di kanan bernilai lebih besar."
        if is_id
        else "On a number line, numbers to the right are greater."
    )

    prerequisites = metadata.get("active_prerequisites")
    if isinstance(prerequisites, list):
        normalized_prerequisites = [
            str(item).strip() for item in prerequisites if str(item).strip()
        ]
    else:
        normalized_prerequisites = list(_PILOT_PREREQUISITES)

    marker_values = _resolve_marker_values(learner_focus_text)
    marker_left, marker_right = marker_values
    marker_min = min(marker_values)
    marker_max = max(marker_values)
    range_min = marker_min - 3
    range_max = marker_max + 3

    spec_json: dict[str, Any] = {
        "id": f"context_auto_{workspace.id}",
        "node_id": node_id or _PILOT_NODE_ID,
        "template_id": _PILOT_TEMPLATE_ID,
        "phase": "D",
        "audience_level": "smp",
        "language": normalized_language,
        "title": title,
        "subtitle": subtitle,
        "number_range": {"min": range_min, "max": range_max, "step": 1},
        "markers": [
            {"value": marker_left, "label": str(marker_left)},
            {"value": marker_right, "label": str(marker_right)},
        ],
        "highlight_values": [marker_left, marker_right],
        "operation": {
            "type": "compare",
            "from": marker_left,
            "to": marker_right,
            "label": (
                f"{marker_right} lebih besar dari {marker_left}"
                if is_id
                else f"{marker_right} is greater than {marker_left}"
            ),
        },
        "steps": [
            {
                "title": "Lihat posisi angka" if is_id else "Check positions",
                "body": (
                    f"{marker_left} berada di kiri, sedangkan {marker_right} berada di kanan."
                    if is_id
                    else f"{marker_left} is on the left, while {marker_right} is on the right."
                ),
                "narration": step_1_narration,
            },
            {
                "title": "Bandingkan nilai" if is_id else "Compare values",
                "body": (
                    "Angka di kanan pada garis bilangan nilainya lebih besar."
                    if is_id
                    else "A number farther right on the number line has a larger value."
                ),
                "narration": step_2_narration,
            },
        ],
        "summary": summary,
        "voiceover_script": intro,
        "intro_narration": intro,
        "summary_narration": summary,
        "narration_segments": [
            {"slot": "intro", "text": intro},
            {"slot": "step", "step_index": 1, "text": step_1_narration},
            {"slot": "step", "step_index": 2, "text": step_2_narration},
            {"slot": "summary", "text": summary},
        ],
    }

    debug_meta: dict[str, Any] = {
        "spec_source": "context_auto_backend",
        "resolved_node_id": node_id or _PILOT_NODE_ID,
        "resolved_concept_type": concept_type,
        "resolved_template_id": _PILOT_TEMPLATE_ID,
        "resolved_prerequisites": normalized_prerequisites,
        "context_source": metadata.get("context_source"),
        "language": normalized_language,
        "learner_focus_text": learner_focus_text,
    }

    return WorkspaceGeneratedSpec(
        template_id=_PILOT_TEMPLATE_ID,
        spec_json=spec_json,
        debug_meta=debug_meta,
    )


def _normalize_language(language: str) -> str:
    normalized = str(language or "").strip().lower()
    if not normalized:
        return "id"
    aliases = {
        "indonesian": "id",
        "bahasa": "id",
        "english": "en",
        "en-us": "en",
        "id-id": "id",
    }
    normalized = aliases.get(normalized, normalized)
    if "-" in normalized:
        base = normalized.split("-", 1)[0]
        if base:
            normalized = base
    return normalized[:16] or "id"


def _latest_learner_focus_text(workspace: WorkspaceSession) -> str:
    events = list(workspace.events or [])
    for event in reversed(events):
        if str(event.actor_type).strip().lower() != "learner":
            continue
        text = str(event.text_payload or "").strip()
        if text:
            return text
    return ""


def _resolve_marker_values(learner_focus_text: str) -> tuple[int, int]:
    if learner_focus_text:
        matches = re.findall(r"(?<!\d)-?\d+(?!\d)", learner_focus_text)
        parsed: list[int] = []
        for match in matches:
            try:
                value = int(match)
            except ValueError:
                continue
            if value not in parsed:
                parsed.append(value)
        if len(parsed) >= 2:
            first, second = parsed[0], parsed[1]
            left, right = sorted((first, second))
            if left == right:
                return left - 1, right + 1
            return left, right
    return -2, 3
