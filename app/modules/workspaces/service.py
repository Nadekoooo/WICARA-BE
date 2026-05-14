from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.learning.models import LearningTrack, MediaArtifact, TrackModule
from app.modules.learning.service import media_artifact_to_schema
from app.modules.workspaces.models import WorkspaceEvent, WorkspaceSession
from app.modules.workspaces.schemas import (
    WorkspaceEventCreateResponse,
    WorkspaceEventRead,
    WorkspaceRead,
)

VALID_EVENT_TYPES = {
    "text",
    "quiz_answer",
    "canvas_sent",
    "media_generated",
    "system",
    "note",
}
VALID_ACTOR_TYPES = {"learner", "tutor", "system"}


def create_or_resume_workspace(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
    module_id: UUID,
    content_mode: str,
) -> WorkspaceRead:
    track, module = _resolve_owned_track_module(
        session,
        user=user,
        track_id=track_id,
        module_id=module_id,
    )
    workspace = session.scalar(
        select(WorkspaceSession)
        .where(
            WorkspaceSession.user_id == user.id,
            WorkspaceSession.track_id == track.id,
            WorkspaceSession.module_id == module.id,
        )
        .options(selectinload(WorkspaceSession.events))
    )
    if workspace is None:
        workspace = WorkspaceSession(
            user_id=user.id,
            track_id=track.id,
            module_id=module.id,
            current_topic=module.title,
            content_mode=_normalize_content_mode(content_mode),
            status="active",
            metadata_json={"source": "workspace_api"},
        )
        session.add(workspace)
    else:
        workspace.current_topic = module.title
        workspace.content_mode = _normalize_content_mode(content_mode)
        workspace.status = "active"
        workspace.updated_at = datetime.now(UTC)

    session.commit()
    workspace = _load_workspace(session, user=user, workspace_id=workspace.id)
    assert workspace is not None
    return workspace_to_schema(session, workspace)


def read_workspace(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID,
) -> WorkspaceRead | None:
    workspace = _load_workspace(session, user=user, workspace_id=workspace_id)
    return workspace_to_schema(session, workspace) if workspace else None


def append_workspace_event(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID,
    event_type: str,
    actor_type: str,
    text_payload: str,
    canvas_snapshot_id: UUID | None,
    media_artifact_id: UUID | None,
    metadata: dict[str, Any],
) -> WorkspaceEventCreateResponse | None:
    workspace = _load_workspace(session, user=user, workspace_id=workspace_id)
    if workspace is None:
        return None

    normalized_event_type = _normalize_event_type(event_type)
    normalized_actor_type = _normalize_actor_type(actor_type)
    if media_artifact_id is not None:
        _resolve_owned_media_artifact(session, user=user, media_artifact_id=media_artifact_id)

    event = WorkspaceEvent(
        workspace_session_id=workspace.id,
        event_type=normalized_event_type,
        actor_type=normalized_actor_type,
        text_payload=text_payload.strip(),
        canvas_snapshot_id=canvas_snapshot_id,
        media_artifact_id=media_artifact_id,
        metadata_json=metadata,
    )
    workspace.updated_at = datetime.now(UTC)
    session.add(event)
    session.commit()
    session.refresh(event)

    workspace = _load_workspace(session, user=user, workspace_id=workspace.id)
    assert workspace is not None
    return WorkspaceEventCreateResponse(
        event=event_to_schema(event),
        tutor_response=None,
        workspace=workspace_to_schema(session, workspace),
    )


def workspace_to_schema(session: Session, workspace: WorkspaceSession) -> WorkspaceRead:
    events = sorted(
        workspace.events,
        key=lambda event: event.created_at or datetime.min.replace(tzinfo=UTC),
    )
    latest_media = _latest_media_artifact(session, events)
    return WorkspaceRead(
        id=workspace.id,
        track_id=workspace.track_id,
        module_id=workspace.module_id,
        current_topic=workspace.current_topic,
        content_mode=workspace.content_mode,
        status=workspace.status,
        events=[event_to_schema(event) for event in events],
        last_canvas_snapshot_id=_latest_canvas_snapshot_id(events),
        latest_media=media_artifact_to_schema(latest_media) if latest_media else None,
    )


def event_to_schema(event: WorkspaceEvent) -> WorkspaceEventRead:
    return WorkspaceEventRead(
        id=event.id,
        workspace_id=event.workspace_session_id,
        event_type=event.event_type,
        actor_type=event.actor_type,
        text_payload=event.text_payload,
        canvas_snapshot_id=event.canvas_snapshot_id,
        media_artifact_id=event.media_artifact_id,
        metadata=event.metadata_json or {},
        created_at=event.created_at.isoformat() if event.created_at else "",
    )


def _resolve_owned_track_module(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
    module_id: UUID,
) -> tuple[LearningTrack, TrackModule]:
    track = session.scalar(
        select(LearningTrack)
        .where(LearningTrack.id == track_id, LearningTrack.user_id == user.id)
        .options(selectinload(LearningTrack.modules))
    )
    if track is None:
        raise LookupError("Track was not found.")

    module = next((item for item in track.modules if item.id == module_id), None)
    if module is None:
        raise LookupError("Track module was not found.")
    return track, module


def _resolve_owned_media_artifact(
    session: Session,
    *,
    user: UserAccount,
    media_artifact_id: UUID,
) -> MediaArtifact:
    artifact = session.scalar(
        select(MediaArtifact).where(
            MediaArtifact.id == media_artifact_id,
            MediaArtifact.user_id == user.id,
        )
    )
    if artifact is None:
        raise LookupError("Media artifact was not found.")
    return artifact


def _load_workspace(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID,
) -> WorkspaceSession | None:
    return session.scalar(
        select(WorkspaceSession)
        .where(WorkspaceSession.id == workspace_id, WorkspaceSession.user_id == user.id)
        .options(selectinload(WorkspaceSession.events))
        .execution_options(populate_existing=True)
    )


def _normalize_event_type(event_type: str) -> str:
    normalized = event_type.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in VALID_EVENT_TYPES:
        raise ValueError(
            "Event type must be text, quiz_answer, canvas_sent, media_generated, system, or note."
        )
    return normalized


def _normalize_actor_type(actor_type: str) -> str:
    normalized = actor_type.strip().lower()
    if normalized not in VALID_ACTOR_TYPES:
        raise ValueError("Actor type must be learner, tutor, or system.")
    return normalized


def _normalize_content_mode(content_mode: str) -> str:
    normalized = content_mode.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized or "chat"


def _latest_canvas_snapshot_id(events: list[WorkspaceEvent]) -> UUID | None:
    for event in reversed(events):
        if event.canvas_snapshot_id is not None:
            return event.canvas_snapshot_id
    return None


def _latest_media_artifact(
    session: Session,
    events: list[WorkspaceEvent],
) -> MediaArtifact | None:
    for event in reversed(events):
        if event.media_artifact_id is not None:
            return session.get(MediaArtifact, event.media_artifact_id)
    return None
