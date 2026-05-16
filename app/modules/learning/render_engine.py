from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from app.core.config import Settings, get_settings, resolve_project_path


@dataclass(frozen=True)
class RenderOutput:
    video_path: str
    relative_video_path: str
    stdout: str
    stderr: str


class RenderEngineError(RuntimeError):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


def render_template_scene(
    *,
    job_id: UUID,
    template_path: str,
    scene_class: str,
    spec_json: dict[str, Any],
    language: str | None = None,
    quality_profile: str,
    timeout_seconds: int | None = None,
    settings: Settings | None = None,
) -> RenderOutput:
    resolved_settings = settings or get_settings()
    output_root = resolve_project_path(resolved_settings.media_render_output_dir)
    workspace_dir = output_root / str(job_id)
    render_workdir = workspace_dir / "work"
    media_dir = workspace_dir / "media"
    render_workdir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    _project_root = Path(__file__).resolve().parent.parent.parent.parent
    template_file = (_project_root / template_path).resolve()
    if not template_file.exists():
        raise RenderEngineError(
            code="render_error",
            message=f"Template file does not exist: {template_file}",
            details={"template_path": str(template_file)},
        )
    if not template_file.is_file():
        raise RenderEngineError(
            code="render_error",
            message=f"Template path is not a file: {template_file}",
            details={"template_path": str(template_file)},
        )

    templates_dir = template_file.parent
    core_templates = templates_dir / "core_templates.py"
    base_scene = templates_dir / "base_scene.py"
    for required in (core_templates, base_scene):
        if not required.exists():
            raise RenderEngineError(
                code="render_error",
                message=f"Missing required template runtime file: {required.name}",
                details={"missing_file": str(required)},
            )

    for stale_file in (
        render_workdir / "core_templates.py",
        render_workdir / "base_scene.py",
        render_workdir / "generated_template.py",
        render_workdir / "render_scene.py",
    ):
        stale_file.unlink(missing_ok=True)
    shutil.rmtree(render_workdir / "__pycache__", ignore_errors=True)

    shutil.copyfile(core_templates, render_workdir / "core_templates.py")
    shutil.copyfile(base_scene, render_workdir / "base_scene.py")
    shutil.copyfile(template_file, render_workdir / "generated_template.py")

    normalized_language = str(language or "").strip().lower()
    spec_payload = dict(spec_json)
    if normalized_language and not spec_payload.get("language"):
        spec_payload["language"] = normalized_language
        spec_payload.setdefault("locale", normalized_language)
    spec_payload = _inject_runtime_tts_spec(
        spec_payload=spec_payload,
        settings=resolved_settings,
    )

    render_scene_path = render_workdir / "render_scene.py"
    spec_repr = repr(spec_payload)
    render_scene_path.write_text(
        (
            "from generated_template import GeneratedTemplate\n\n"
            "class RenderScene(GeneratedTemplate):\n"
            f"    SPEC = {spec_repr}\n"
        ),
        encoding="utf-8",
    )

    timeout = timeout_seconds or resolved_settings.media_render_timeout_seconds
    manim_quality_flag = _quality_profile_to_manim_flag(quality_profile)
    cmd = [
        sys.executable,
        "-m",
        "manim",
        manim_quality_flag,
        str(render_scene_path),
        "RenderScene",
        "--media_dir",
        str(media_dir),
        "--disable_caching",
    ]
    render_env = _build_render_env(resolved_settings)
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(render_workdir),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=render_env,
        )
    except subprocess.TimeoutExpired as exc:
        raise RenderEngineError(
            code="render_timeout",
            message=f"Manim render timed out after {timeout} seconds.",
            details={
                "timeout_seconds": timeout,
                "template_path": str(template_file),
                "scene_class": scene_class,
            },
        ) from exc

    if completed.returncode != 0:
        raise RenderEngineError(
            code="render_error",
            message="Manim render command failed.",
            details={
                "return_code": completed.returncode,
                "stdout": _tail_text(completed.stdout),
                "stderr": _tail_text(completed.stderr),
                "template_path": str(template_file),
                "scene_class": scene_class,
            },
        )

    video_path = _find_rendered_video(media_dir=media_dir)
    if video_path is None:
        raise RenderEngineError(
            code="render_error",
            message="Manim render finished but output MP4 was not found.",
            details={"media_dir": str(media_dir)},
        )

    relative_video_path = str(video_path.relative_to(output_root))
    return RenderOutput(
        video_path=str(video_path),
        relative_video_path=relative_video_path.replace("\\", "/"),
        stdout=_tail_text(completed.stdout),
        stderr=_tail_text(completed.stderr),
    )


def _inject_runtime_tts_spec(*, spec_payload: dict[str, Any], settings: Settings) -> dict[str, Any]:
    payload = dict(spec_payload)
    explicit_provider = str(
        payload.get("tts_provider") or payload.get("voiceover_provider") or ""
    ).strip()
    if not explicit_provider:
        provider_from_settings = str(settings.media_tts_provider or "").strip().lower()
        if provider_from_settings == "gtts_voiceover" and settings.openai_api_key:
            payload["tts_provider"] = "openai_voiceover"
        else:
            payload["tts_provider"] = settings.media_tts_provider

    provider = str(payload.get("tts_provider") or "").strip().lower()
    if provider == "openai_voiceover":
        payload.setdefault("tts_model_primary", settings.media_openai_tts_model_primary)
        payload.setdefault("tts_model_fallback", settings.media_openai_tts_model_fallback)
        payload.setdefault("tts_voice_primary", settings.media_openai_tts_voice_primary)
        payload.setdefault("tts_voice_fallback", settings.media_openai_tts_voice_fallback)
        payload.setdefault("tts_response_format", settings.media_openai_tts_response_format)
        payload.setdefault("tts_instructions", settings.media_openai_tts_instructions)
    return payload


def _build_render_env(settings: Settings) -> dict[str, str]:
    env = dict(os.environ)
    env["MEDIA_TTS_PROVIDER"] = settings.media_tts_provider
    env["MEDIA_OPENAI_TTS_MODEL_PRIMARY"] = settings.media_openai_tts_model_primary
    env["MEDIA_OPENAI_TTS_MODEL_FALLBACK"] = settings.media_openai_tts_model_fallback
    env["MEDIA_OPENAI_TTS_VOICE_PRIMARY"] = settings.media_openai_tts_voice_primary
    env["MEDIA_OPENAI_TTS_VOICE_FALLBACK"] = settings.media_openai_tts_voice_fallback
    env["MEDIA_OPENAI_TTS_RESPONSE_FORMAT"] = settings.media_openai_tts_response_format
    env["MEDIA_OPENAI_TTS_INSTRUCTIONS"] = settings.media_openai_tts_instructions or ""
    if settings.openai_api_key:
        env["OPENAI_API_KEY"] = settings.openai_api_key
    return env


def _quality_profile_to_manim_flag(profile: str) -> str:
    normalized = profile.strip().lower()
    mapping = {
        "low": "-ql",
        "standard": "-qm",
        "medium": "-qm",
        "high": "-qh",
        "ultra": "-qk",
        "l": "-ql",
        "m": "-qm",
        "h": "-qh",
        "k": "-qk",
    }
    if normalized in mapping:
        return mapping[normalized]
    if normalized.startswith("-q") and len(normalized) == 3:
        return normalized
    return "-qm"


def _find_rendered_video(*, media_dir: Path) -> Path | None:
    candidates = sorted(
        media_dir.rglob("RenderScene.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    any_mp4 = sorted(
        media_dir.rglob("*.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return any_mp4[0] if any_mp4 else None


def _tail_text(value: str, max_chars: int = 2000) -> str:
    text = value.strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]
