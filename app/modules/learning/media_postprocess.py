from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from app.core.config import Settings, get_settings
from app.modules.learning.models import MediaArtifact
from app.modules.learning.render_engine import RenderOutput


@dataclass(frozen=True)
class MediaPostprocessOutput:
    video_path: str
    relative_video_path: str
    thumbnail_path: str
    relative_thumbnail_path: str
    duration_seconds: int
    transcript: str
    voiceover_script: str
    audio_path: str | None
    relative_audio_path: str | None
    quality_gate: dict[str, Any]
    tts_meta: dict[str, Any]
    ffmpeg_meta: dict[str, Any]


class MediaPostprocessError(RuntimeError):
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


def postprocess_render_output(
    *,
    job_id: UUID,
    artifact: MediaArtifact,
    render_output: RenderOutput,
    settings: Settings | None = None,
) -> MediaPostprocessOutput:
    resolved_settings = settings or get_settings()
    output_root = (Path.cwd() / resolved_settings.media_render_output_dir).resolve()
    workspace_dir = output_root / str(job_id)
    final_dir = workspace_dir / "final"
    final_dir.mkdir(parents=True, exist_ok=True)

    source_video_path = Path(render_output.video_path).resolve()
    if not source_video_path.exists():
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="Rendered video file is missing before post-process.",
            details={"video_path": str(source_video_path)},
        )

    voiceover_script = _build_voiceover_script(artifact.spec_json)
    tts_meta: dict[str, Any] = {
        "provider": resolved_settings.media_tts_provider,
        "required": bool(resolved_settings.media_tts_required),
        "mode": "template_voiceover",
        "enabled": False,
        "audio_stream_present": False,
        "warning": None,
    }

    final_video_path = final_dir / "final_video.mp4"
    ffmpeg_completed = _finalize_video_with_ffmpeg(
        source_video_path=source_video_path,
        output_video_path=final_video_path,
        settings=resolved_settings,
    )

    thumbnail_path = final_dir / "thumbnail.jpg"
    thumbnail_completed = _extract_thumbnail_with_ffmpeg(
        video_path=final_video_path,
        thumbnail_path=thumbnail_path,
        settings=resolved_settings,
    )

    duration_raw, ffprobe_stdout = _probe_video_duration_seconds(
        video_path=final_video_path,
        settings=resolved_settings,
    )
    duration_seconds = max(0, int(round(duration_raw)))
    audio_stream_present, ffprobe_audio_stdout = _probe_video_audio_stream(
        video_path=final_video_path,
        settings=resolved_settings,
    )

    if voiceover_script and resolved_settings.media_tts_provider != "none":
        tts_meta["enabled"] = True
    if resolved_settings.media_tts_provider == "none":
        tts_meta["warning"] = "TTS provider is disabled; video may contain no narration."
    if resolved_settings.media_tts_required and not voiceover_script:
        raise MediaPostprocessError(
            code="tts_error",
            message="TTS is required but no voiceover_script was found in spec_json.",
            details={"template_id": artifact.template_id},
        )
    if resolved_settings.media_tts_required and resolved_settings.media_tts_provider == "none":
        raise MediaPostprocessError(
            code="tts_error",
            message="TTS is required but MEDIA_TTS_PROVIDER is set to 'none'.",
            details={"provider": resolved_settings.media_tts_provider},
        )
    if resolved_settings.media_tts_required and not audio_stream_present:
        raise MediaPostprocessError(
            code="tts_error",
            message="TTS is required but rendered video does not contain an audio stream.",
            details={"video_path": str(final_video_path)},
        )
    if tts_meta["enabled"] and not audio_stream_present:
        tts_meta["warning"] = "Voiceover script exists but output video has no audio stream."
    tts_meta["audio_stream_present"] = audio_stream_present

    quality_gate = _evaluate_duration_policy(
        spec_json=artifact.spec_json,
        duration_seconds=duration_seconds,
        settings=resolved_settings,
    )
    if quality_gate["result"] == "failed":
        raise MediaPostprocessError(
            code="duration_policy_error",
            message=str(quality_gate.get("message") or "Duration policy failed."),
            details=quality_gate,
        )

    relative_video_path = _to_relative_path(final_video_path, output_root)
    relative_thumbnail_path = _to_relative_path(thumbnail_path, output_root)

    ffmpeg_meta = {
        "finalize_stdout": _tail_text(ffmpeg_completed.stdout),
        "finalize_stderr": _tail_text(ffmpeg_completed.stderr),
        "thumbnail_stdout": _tail_text(thumbnail_completed.stdout),
        "thumbnail_stderr": _tail_text(thumbnail_completed.stderr),
        "ffprobe_stdout": _tail_text(ffprobe_stdout),
        "ffprobe_audio_stdout": _tail_text(ffprobe_audio_stdout),
        "duration_seconds_raw": duration_raw,
    }

    return MediaPostprocessOutput(
        video_path=str(final_video_path),
        relative_video_path=relative_video_path,
        thumbnail_path=str(thumbnail_path),
        relative_thumbnail_path=relative_thumbnail_path,
        duration_seconds=duration_seconds,
        transcript=voiceover_script,
        voiceover_script=voiceover_script,
        audio_path=None,
        relative_audio_path=None,
        quality_gate=quality_gate,
        tts_meta=tts_meta,
        ffmpeg_meta=ffmpeg_meta,
    )


def _finalize_video_with_ffmpeg(
    *,
    source_video_path: Path,
    output_video_path: Path,
    settings: Settings,
) -> subprocess.CompletedProcess[str]:
    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.media_ffmpeg_binary,
        "-y",
        "-i",
        str(source_video_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        str(output_video_path),
    ]
    return _run_command(
        cmd=cmd,
        timeout_seconds=settings.media_postprocess_timeout_seconds,
        error_code="ffmpeg_error",
        step_name="Video finalization",
    )


def _extract_thumbnail_with_ffmpeg(
    *,
    video_path: Path,
    thumbnail_path: Path,
    settings: Settings,
) -> subprocess.CompletedProcess[str]:
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.media_ffmpeg_binary,
        "-y",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        str(thumbnail_path),
    ]
    completed = _run_command(
        cmd=cmd,
        timeout_seconds=settings.media_postprocess_timeout_seconds,
        error_code="ffmpeg_error",
        step_name="Thumbnail extraction",
    )
    if not thumbnail_path.exists() or thumbnail_path.stat().st_size <= 0:
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="Thumbnail extraction finished without output file.",
            details={"thumbnail_path": str(thumbnail_path)},
        )
    return completed


def _probe_video_duration_seconds(
    *,
    video_path: Path,
    settings: Settings,
) -> tuple[float, str]:
    cmd = [
        settings.media_ffprobe_binary,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    completed = _run_command(
        cmd=cmd,
        timeout_seconds=settings.media_postprocess_timeout_seconds,
        error_code="ffmpeg_error",
        step_name="Video duration probe",
    )
    duration = _parse_duration_from_ffprobe(completed.stdout)
    if duration <= 0:
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="FFprobe returned invalid video duration.",
            details={"stdout": _tail_text(completed.stdout)},
        )
    return duration, completed.stdout


def _probe_video_audio_stream(
    *,
    video_path: Path,
    settings: Settings,
) -> tuple[bool, str]:
    cmd = [
        settings.media_ffprobe_binary,
        "-v",
        "error",
        "-select_streams",
        "a",
        "-show_entries",
        "stream=index",
        "-of",
        "json",
        str(video_path),
    ]
    completed = _run_command(
        cmd=cmd,
        timeout_seconds=settings.media_postprocess_timeout_seconds,
        error_code="ffmpeg_error",
        step_name="Audio stream probe",
    )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="Failed to parse ffprobe audio stream output.",
            details={"stdout": _tail_text(completed.stdout)},
        ) from exc
    streams = payload.get("streams")
    has_audio = isinstance(streams, list) and len(streams) > 0
    return has_audio, completed.stdout


def _parse_duration_from_ffprobe(output: str) -> float:
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="Failed to parse ffprobe JSON output.",
            details={"stdout": _tail_text(output)},
        ) from exc

    duration_value = payload.get("format", {}).get("duration")
    try:
        return float(duration_value)
    except (TypeError, ValueError) as exc:
        raise MediaPostprocessError(
            code="ffmpeg_error",
            message="FFprobe output did not contain valid format.duration.",
            details={"stdout": _tail_text(output)},
        ) from exc


def _evaluate_duration_policy(
    *,
    spec_json: dict[str, Any],
    duration_seconds: int,
    settings: Settings,
) -> dict[str, Any]:
    audience_level = str(spec_json.get("audience_level", "")).strip().lower() or "default"
    minimum_seconds = _minimum_duration_seconds_for_audience(
        settings=settings,
        audience_level=audience_level,
    )
    mode = settings.media_duration_policy_mode

    gate = {
        "mode": mode,
        "audience_level": audience_level,
        "minimum_seconds": minimum_seconds,
        "actual_seconds": duration_seconds,
        "passed": duration_seconds >= minimum_seconds,
        "result": "pass",
        "message": "Duration policy passed.",
    }

    if mode == "off":
        gate.update(
            {
                "result": "skipped",
                "message": "Duration policy is disabled.",
            }
        )
        return gate

    if duration_seconds >= minimum_seconds:
        return gate

    if mode == "soft_fail":
        gate.update(
            {
                "result": "warning",
                "message": (
                    "Duration is below minimum policy but allowed by soft_fail mode."
                ),
            }
        )
        return gate

    gate.update(
        {
            "result": "failed",
            "message": "Duration is below minimum policy and blocked by hard_fail mode.",
        }
    )
    return gate


def _minimum_duration_seconds_for_audience(
    *,
    settings: Settings,
    audience_level: str,
) -> int:
    normalized = audience_level.strip().lower()
    if normalized in {"sd", "elementary"}:
        return settings.media_duration_min_seconds_sd
    if normalized in {"smp", "junior", "middle"}:
        return settings.media_duration_min_seconds_smp
    if normalized in {"sma", "high", "senior"}:
        return settings.media_duration_min_seconds_sma
    return settings.media_duration_min_seconds_default


def _build_voiceover_script(spec_json: dict[str, Any]) -> str:
    explicit = _clean_text(spec_json.get("voiceover_script"))
    if explicit:
        return explicit

    sections: list[str] = []
    sections.append(_clean_text(spec_json.get("title")))
    sections.append(_clean_text(spec_json.get("subtitle")))

    raw_steps = spec_json.get("steps")
    if isinstance(raw_steps, list):
        for step in raw_steps:
            if not isinstance(step, dict):
                continue
            title = _clean_text(step.get("title"))
            body = _clean_text(step.get("body"))
            combined = " ".join(part for part in [title, body] if part)
            if combined:
                sections.append(combined)

    sections.append(_clean_text(spec_json.get("summary")))
    script = " ".join(part for part in sections if part)
    return script[:6000]


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = " ".join(str(value).split())
    return text.strip()


def _to_relative_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(resolved)


def _run_command(
    *,
    cmd: list[str],
    timeout_seconds: int,
    error_code: str,
    step_name: str,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MediaPostprocessError(
            code=error_code,
            message=f"{step_name} timed out after {timeout_seconds} seconds.",
            details={
                "command": cmd,
                "timeout_seconds": timeout_seconds,
            },
        ) from exc
    except FileNotFoundError as exc:
        raise MediaPostprocessError(
            code=error_code,
            message=f"Binary for {step_name} was not found.",
            details={"command": cmd},
        ) from exc

    if completed.returncode != 0:
        raise MediaPostprocessError(
            code=error_code,
            message=f"{step_name} command failed.",
            details={
                "command": cmd,
                "return_code": completed.returncode,
                "stdout": _tail_text(completed.stdout),
                "stderr": _tail_text(completed.stderr),
            },
        )
    return completed


def _tail_text(value: str, max_chars: int = 2000) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]
