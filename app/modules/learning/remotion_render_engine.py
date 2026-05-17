from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from app.core.config import Settings, get_settings, resolve_project_path


@dataclass(frozen=True)
class RemotionRenderOutput:
    video_path: str
    relative_video_path: str
    stdout: str
    stderr: str


class RemotionRenderError(RuntimeError):
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


def render_template_scene_remotion(
    *,
    job_id: UUID,
    template_id: str,
    template_path: str,
    spec_json: dict[str, Any],
    language: str | None = None,
    quality_profile: str,
    runtime: dict[str, Any] | None = None,
    timeout_seconds: int | None = None,
    settings: Settings | None = None,
) -> RemotionRenderOutput:
    resolved_settings = settings or get_settings()
    output_root = resolve_project_path(resolved_settings.media_render_output_dir)
    workspace_dir = output_root / str(job_id)
    media_dir = workspace_dir / "media" / "remotion"
    media_dir.mkdir(parents=True, exist_ok=True)

    runtime_payload = dict(runtime or {})
    project_dir = _resolve_remotion_project_dir(
        runtime=runtime_payload,
        settings=resolved_settings,
        template_path=template_path,
    )
    entry_path = _resolve_remotion_entry_path(
        runtime=runtime_payload,
        settings=resolved_settings,
        project_dir=project_dir,
        template_path=template_path,
    )
    composition_id = _resolve_composition_id(
        runtime=runtime_payload,
        template_id=template_id,
        spec_json=spec_json,
    )

    output_video_path = media_dir / "RenderScene.mp4"
    output_video_path.unlink(missing_ok=True)

    props_payload = dict(spec_json or {})
    props_payload["template_id"] = template_id
    if language and not props_payload.get("language"):
        props_payload["language"] = str(language).strip().lower()

    props_json = json.dumps(props_payload, ensure_ascii=False)
    timeout = timeout_seconds or resolved_settings.media_remotion_timeout_seconds
    node_binary = _resolve_node_binary(resolved_settings.media_node_binary)
    remotion_cli_script = _resolve_remotion_cli_script(project_dir)
    npx_binary = _resolve_npx_binary(resolved_settings.media_npx_binary)
    if remotion_cli_script:
        cmd = [
            node_binary,
            remotion_cli_script,
            "render",
            str(entry_path),
            composition_id,
            str(output_video_path),
            "--props",
            props_json,
            "--concurrency",
            str(resolved_settings.media_remotion_concurrency),
        ]
    else:
        cmd = [
            npx_binary,
            "remotion",
            "render",
            str(entry_path),
            composition_id,
            str(output_video_path),
            "--props",
            props_json,
            "--concurrency",
            str(resolved_settings.media_remotion_concurrency),
        ]

    try:
        completed = subprocess.run(
            cmd,
            cwd=str(project_dir),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
            env=_build_remotion_env(resolved_settings),
        )
    except subprocess.TimeoutExpired as exc:
        raise RemotionRenderError(
            code="render_timeout",
            message=f"Remotion render timed out after {timeout} seconds.",
            details={
                "timeout_seconds": timeout,
                "template_id": template_id,
                "composition_id": composition_id,
                "project_dir": str(project_dir),
                "entry_path": str(entry_path),
            },
        ) from exc
    except FileNotFoundError as exc:
        raise RemotionRenderError(
            code="render_error",
            message="Remotion render command is not available in PATH.",
            details={
                "binary": " ".join(cmd[:2]),
                "project_dir": str(project_dir),
            },
        ) from exc

    if completed.returncode != 0:
        raise RemotionRenderError(
            code="render_error",
            message="Remotion render command failed.",
            details={
                "return_code": completed.returncode,
                "stdout": _tail_text(completed.stdout),
                "stderr": _tail_text(completed.stderr),
                "template_id": template_id,
                "composition_id": composition_id,
                "project_dir": str(project_dir),
                "entry_path": str(entry_path),
                "binary": " ".join(cmd[:2]),
            },
        )

    if not output_video_path.exists():
        raise RemotionRenderError(
            code="render_error",
            message="Remotion render finished but output MP4 was not found.",
            details={
                "template_id": template_id,
                "composition_id": composition_id,
                "output_video_path": str(output_video_path),
            },
        )

    relative_video_path = str(output_video_path.relative_to(output_root)).replace("\\", "/")
    return RemotionRenderOutput(
        video_path=str(output_video_path),
        relative_video_path=relative_video_path,
        stdout=_tail_text(completed.stdout),
        stderr=_tail_text(completed.stderr),
    )


def _resolve_remotion_project_dir(
    *,
    runtime: dict[str, Any],
    settings: Settings,
    template_path: str,
) -> Path:
    runtime_project_dir = str(runtime.get("project_dir") or "").strip()
    if runtime_project_dir:
        project_dir = resolve_project_path(runtime_project_dir)
        if project_dir.exists():
            return project_dir

    project_dir = resolve_project_path(settings.media_remotion_project_dir)
    if project_dir.exists():
        return project_dir

    # Fallback: derive from template_path if it points to .../src/index.ts
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    template_file = (project_root / template_path).resolve()
    if template_file.exists():
        return template_file.parent.parent

    raise RemotionRenderError(
        code="render_error",
        message="Remotion project directory does not exist.",
        details={
            "runtime_project_dir": runtime_project_dir,
            "configured_project_dir": settings.media_remotion_project_dir,
            "template_path": template_path,
        },
    )


def _resolve_remotion_entry_path(
    *,
    runtime: dict[str, Any],
    settings: Settings,
    project_dir: Path,
    template_path: str,
) -> Path:
    runtime_entry = str(runtime.get("entry_point") or "").strip()
    entry_token = runtime_entry or str(settings.media_remotion_entry or "").strip()
    if not entry_token:
        raise RemotionRenderError(
            code="render_error",
            message="Remotion entry point is missing.",
            details={"project_dir": str(project_dir)},
        )

    entry_path = Path(entry_token)
    if not entry_path.is_absolute():
        entry_path = (project_dir / entry_path).resolve()
    if entry_path.exists():
        return entry_path

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    template_file = (project_root / template_path).resolve()
    if template_file.exists():
        return template_file

    raise RemotionRenderError(
        code="render_error",
        message="Remotion entry file does not exist.",
        details={
            "entry_point": entry_token,
            "project_dir": str(project_dir),
            "template_path": template_path,
        },
    )


def _resolve_composition_id(
    *,
    runtime: dict[str, Any],
    template_id: str,
    spec_json: dict[str, Any],
) -> str:
    composition_id = _normalize_composition_id(str(runtime.get("composition_id") or "").strip())
    if composition_id:
        return composition_id

    row_index = spec_json.get("row_index")
    if isinstance(row_index, int):
        return _normalize_composition_id(f"{row_index:03d}-{template_id}")

    raise RemotionRenderError(
        code="render_error",
        message="Remotion composition_id is missing in registry runtime metadata.",
        details={"template_id": template_id},
    )


def _build_remotion_env(settings: Settings) -> dict[str, str]:
    env = dict(os.environ)
    if settings.openai_api_key:
        env["OPENAI_API_KEY"] = settings.openai_api_key
    return env


def _resolve_node_binary(configured_binary: str) -> str:
    token = str(configured_binary or "").strip() or "node"
    if shutil.which(token):
        return token
    if os.name == "nt":
        for candidate in (f"{token}.exe", "node.exe"):
            if shutil.which(candidate):
                return candidate
    return token


def _resolve_remotion_cli_script(project_dir: Path) -> str | None:
    candidate = project_dir / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
    if candidate.exists():
        return str(candidate.resolve())
    return None


def _resolve_npx_binary(configured_binary: str) -> str:
    token = str(configured_binary or "").strip() or "npx"
    if os.name == "nt":
        # Prefer cmd wrappers because subprocess on Windows cannot execute extensionless shims.
        for candidate in (f"{token}.cmd", "npx.cmd", f"{token}.exe", "npx.exe"):
            if shutil.which(candidate):
                return candidate
        resolved = shutil.which(token)
        if resolved:
            if not Path(resolved).suffix:
                cmd_variant = f"{resolved}.cmd"
                if Path(cmd_variant).exists():
                    return cmd_variant
            return resolved
        return token
    if shutil.which(token):
        return token
    return token


def _tail_text(value: str | None, max_chars: int = 2000) -> str:
    text = (value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def _normalize_composition_id(value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    token = token.replace(".", "-")
    normalized_chars = []
    for ch in token:
        if ch.isalnum() or ch == "-":
            normalized_chars.append(ch)
        else:
            normalized_chars.append("-")
    normalized = "".join(normalized_chars)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")
