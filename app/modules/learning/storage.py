from __future__ import annotations

import mimetypes
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from app.core.config import Settings, get_settings, resolve_project_path


@dataclass(frozen=True)
class MediaStorageUploadOutput:
    video_url: str
    thumbnail_url: str
    storage_backend: str
    object_video_path: str
    object_thumbnail_path: str
    meta: dict[str, Any]


class MediaStorageError(RuntimeError):
    def __init__(
        self,
        *,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = "upload_error"
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


def upload_media_artifact_files(
    *,
    job_id: UUID,
    artifact_id: UUID,
    local_video_path: str,
    local_thumbnail_path: str,
    settings: Settings | None = None,
) -> MediaStorageUploadOutput:
    resolved_settings = settings or get_settings()
    source_video = Path(local_video_path).resolve()
    source_thumbnail = Path(local_thumbnail_path).resolve()

    if not source_video.exists():
        raise MediaStorageError(
            message="Video file for storage upload does not exist.",
            details={"video_path": str(source_video)},
        )
    if not source_thumbnail.exists():
        raise MediaStorageError(
            message="Thumbnail file for storage upload does not exist.",
            details={"thumbnail_path": str(source_thumbnail)},
        )

    object_prefix = f"manim/{artifact_id}/{job_id}"
    object_video_path = f"{object_prefix}/final_video.mp4"
    object_thumbnail_path = f"{object_prefix}/thumbnail.jpg"

    backend = resolved_settings.media_storage_backend
    if backend == "local":
        return _upload_to_local_storage(
            object_video_path=object_video_path,
            object_thumbnail_path=object_thumbnail_path,
            source_video=source_video,
            source_thumbnail=source_thumbnail,
            settings=resolved_settings,
        )
    if backend == "supabase":
        return _upload_to_supabase_storage(
            object_video_path=object_video_path,
            object_thumbnail_path=object_thumbnail_path,
            source_video=source_video,
            source_thumbnail=source_thumbnail,
            settings=resolved_settings,
        )
    raise MediaStorageError(
        message="Unsupported media storage backend.",
        details={"media_storage_backend": backend},
    )


def _upload_to_local_storage(
    *,
    object_video_path: str,
    object_thumbnail_path: str,
    source_video: Path,
    source_thumbnail: Path,
    settings: Settings,
) -> MediaStorageUploadOutput:
    storage_root = resolve_project_path(settings.media_storage_local_dir)
    storage_root.mkdir(parents=True, exist_ok=True)

    target_video = storage_root / object_video_path
    target_thumbnail = storage_root / object_thumbnail_path
    target_video.parent.mkdir(parents=True, exist_ok=True)
    target_thumbnail.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_video, target_video)
    shutil.copy2(source_thumbnail, target_thumbnail)

    video_url = _join_public_url(settings.media_storage_public_base_url, object_video_path)
    thumbnail_url = _join_public_url(settings.media_storage_public_base_url, object_thumbnail_path)
    return MediaStorageUploadOutput(
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        storage_backend="local",
        object_video_path=object_video_path,
        object_thumbnail_path=object_thumbnail_path,
        meta={
            "storage_root": str(storage_root),
            "local_video_path": str(target_video),
            "local_thumbnail_path": str(target_thumbnail),
        },
    )


def _upload_to_supabase_storage(
    *,
    object_video_path: str,
    object_thumbnail_path: str,
    source_video: Path,
    source_thumbnail: Path,
    settings: Settings,
) -> MediaStorageUploadOutput:
    service_role_key = settings.supabase_service_role_key.strip()
    if not service_role_key:
        raise MediaStorageError(
            message="Supabase storage backend requires SUPABASE_SERVICE_ROLE_KEY.",
            details={"backend": "supabase"},
        )

    bucket = settings.media_storage_supabase_bucket.strip()
    if not bucket:
        raise MediaStorageError(
            message="Supabase storage backend requires MEDIA_STORAGE_SUPABASE_BUCKET.",
            details={"backend": "supabase"},
        )

    base_project_url = settings.supabase_project_url.strip().rstrip("/")
    if not base_project_url:
        raise MediaStorageError(
            message="Supabase storage backend requires SUPABASE_PROJECT_URL.",
            details={"backend": "supabase"},
        )
    upload_base = f"{base_project_url}/storage/v1/object/{bucket}"
    public_base = f"{base_project_url}/storage/v1/object/public/{bucket}"

    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "apikey": service_role_key,
        "x-upsert": "true",
    }
    timeout = settings.media_storage_upload_timeout_seconds

    _upload_single_to_supabase(
        upload_url=f"{upload_base}/{quote(object_video_path, safe='/')}",
        source_path=source_video,
        headers=headers,
        timeout_seconds=timeout,
    )
    _upload_single_to_supabase(
        upload_url=f"{upload_base}/{quote(object_thumbnail_path, safe='/')}",
        source_path=source_thumbnail,
        headers=headers,
        timeout_seconds=timeout,
    )

    return MediaStorageUploadOutput(
        video_url=f"{public_base}/{quote(object_video_path, safe='/')}",
        thumbnail_url=f"{public_base}/{quote(object_thumbnail_path, safe='/')}",
        storage_backend="supabase",
        object_video_path=object_video_path,
        object_thumbnail_path=object_thumbnail_path,
        meta={"bucket": bucket},
    )


def _upload_single_to_supabase(
    *,
    upload_url: str,
    source_path: Path,
    headers: dict[str, str],
    timeout_seconds: int,
) -> None:
    content_type, _ = mimetypes.guess_type(str(source_path))
    payload = source_path.read_bytes()
    request_headers = dict(headers)
    request_headers["Content-Type"] = content_type or "application/octet-stream"
    try:
        response = httpx.post(
            upload_url,
            headers=request_headers,
            content=payload,
            timeout=timeout_seconds,
        )
    except httpx.HTTPError as exc:
        raise MediaStorageError(
            message="Supabase storage upload request failed.",
            details={"upload_url": upload_url, "error": str(exc)},
        ) from exc

    if response.status_code >= 300:
        raise MediaStorageError(
            message="Supabase storage upload rejected by server.",
            details={
                "upload_url": upload_url,
                "status_code": response.status_code,
                "response_text": (response.text or "")[:2000],
            },
        )


def _join_public_url(base_url: str, object_path: str) -> str:
    normalized_base = (base_url or "").strip()
    if not normalized_base:
        normalized_base = "/media-storage"
    normalized_path = object_path.replace("\\", "/").lstrip("/")
    if normalized_base.endswith("/"):
        return f"{normalized_base}{normalized_path}"
    return f"{normalized_base}/{normalized_path}"
