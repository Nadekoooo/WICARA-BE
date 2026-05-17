from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.accounts.models import UserAccount
from app.modules.inputs.service import create_workspace_input_event
from app.modules.learning.models import LearningTrack, MediaArtifact, TrackModule
from app.modules.learning.spec_generator import generate_spec_from_workspace_context
from app.modules.learning.service import media_artifact_to_schema, queue_animation_job
from app.modules.workspaces.mastery import WorkspaceMasteryService
from app.modules.workspaces.models import WorkspaceEvent, WorkspaceSession
from app.modules.workspaces.schemas import (
    TutorResponseRead,
    WorkspaceEventCreateResponse,
    WorkspaceEventRead,
    WorkspaceGenerateVideoResponse,
    WorkspaceRead,
    WorkspaceSessionHistoryRead,
    WorkspaceSessionSummaryRead,
)
from app.modules.workspaces.tutor import generate_tutor_response

VALID_EVENT_TYPES = {
    "text",
    "quiz_answer",
    "canvas_sent",
    "media_generated",
    "system",
    "note",
}
VALID_ACTOR_TYPES = {"learner", "tutor", "system"}
_mastery_service = WorkspaceMasteryService()

_PILOT_NODE_ID = "km_d_matematika_bilangan_bulat"
_PILOT_CONCEPT_TYPE = "number_line_quantity_model"
_PILOT_TEMPLATE_ID = "manim.number_line_quantity.v1"
_PILOT_PREREQUISITES = ["km_c_matematika_bilangan_cacah_sampai_1000000"]
_PILOT_CONTEXT_SOURCE = "hardcoded_number_line_pilot"


def create_or_resume_workspace(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
    module_id: UUID,
    content_mode: str,
    workspace_session_id: UUID | None = None,
    start_new_session: bool = False,
) -> WorkspaceRead:
    track, module = _resolve_owned_track_module(
        session,
        user=user,
        track_id=track_id,
        module_id=module_id,
    )

    workspace: WorkspaceSession | None = None
    if workspace_session_id is not None:
        workspace = _load_workspace(session, user=user, workspace_id=workspace_session_id)
        if workspace is None:
            raise LookupError("Workspace session was not found.")
        if workspace.track_id != track.id or workspace.module_id != module.id:
            raise LookupError("Workspace session does not belong to the requested module.")
    elif not start_new_session:
        workspace = session.scalar(
            select(WorkspaceSession)
            .where(
                WorkspaceSession.user_id == user.id,
                WorkspaceSession.track_id == track.id,
                WorkspaceSession.module_id == module.id,
            )
            .order_by(WorkspaceSession.updated_at.desc(), WorkspaceSession.created_at.desc())
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
    _apply_workspace_pilot_context(workspace)
    module.status = "active"
    track.status = "active"

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


def list_workspace_sessions(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
    module_id: UUID,
) -> WorkspaceSessionHistoryRead:
    track, module = _resolve_owned_track_module(
        session,
        user=user,
        track_id=track_id,
        module_id=module_id,
    )
    workspaces = session.scalars(
        select(WorkspaceSession)
        .where(
            WorkspaceSession.user_id == user.id,
            WorkspaceSession.track_id == track.id,
            WorkspaceSession.module_id == module.id,
        )
        .order_by(WorkspaceSession.updated_at.desc(), WorkspaceSession.created_at.desc())
        .options(selectinload(WorkspaceSession.events))
    ).all()
    return WorkspaceSessionHistoryRead(
        sessions=[
            _workspace_session_summary(workspace, fallback_title=module.title)
            for workspace in workspaces
        ]
    )


async def append_workspace_event(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID,
    event_type: str,
    actor_type: str,
    text_payload: str,
    image_asset_id: UUID | None,
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

    module = session.get(TrackModule, workspace.module_id)

    # Call Gemini before saving so audit info goes into event metadata
    tutor_response, ai_audit = await generate_tutor_response(
        workspace=workspace,
        event_type=normalized_event_type,
        text_payload=text_payload,
        events=list(workspace.events),
    )
    if (
        normalized_event_type == "quiz_answer"
        and metadata.get("is_correct") is True
        and tutor_response is not None
    ):
        tutor_response = tutor_response.model_copy(
            update={
                "intent": "recommend_practice",
                "next_actions": ["apply_concept", "answer_quiz"],
            }
        )

    event_metadata = {**dict(metadata), "ai_audit": ai_audit}
    audit_metadata = {
        **metadata,
        **ai_audit,
        "track_id": str(workspace.track_id),
        "module_id": str(workspace.module_id),
        "tutor_policy": ai_audit.get("ai_source", "unknown"),
    }
    mastery_result = _mastery_service.apply_event(
        session,
        user=user,
        module=module,
        event_type=normalized_event_type,
        text_payload=text_payload,
        metadata=audit_metadata,
    )
    if mastery_result.concept_id is not None:
        audit_metadata["concept_id"] = str(mastery_result.concept_id)
    if mastery_result.update is not None:
        audit_metadata["mastery_update_reason"] = mastery_result.update.reason

    input_event = create_workspace_input_event(
        session,
        user=user,
        workspace_session_id=workspace.id,
        concept_id=mastery_result.concept_id,
        source_event_type=normalized_event_type,
        actor_type=normalized_actor_type,
        text_payload=text_payload,
        image_asset_id=image_asset_id,
        media_artifact_id=media_artifact_id,
        metadata=audit_metadata,
    )
    event = WorkspaceEvent(
        workspace_session_id=workspace.id,
        event_index=_next_event_index(session, workspace_id=workspace.id),
        event_type=normalized_event_type,
        actor_type=normalized_actor_type,
        text_payload=text_payload.strip(),
        image_asset_id=image_asset_id,
        media_artifact_id=media_artifact_id,
        input_event_id=input_event.id,
        metadata_json=event_metadata,
    )
    tutor_event: WorkspaceEvent | None = None
    if tutor_response is not None and tutor_response.text.strip():
        tutor_event = WorkspaceEvent(
            workspace_session_id=workspace.id,
            event_index=event.event_index + 1,
            event_type="text",
            actor_type="tutor",
            text_payload=tutor_response.text.strip(),
            image_asset_id=None,
            media_artifact_id=None,
            input_event_id=None,
            metadata_json={
                "source": "workspace_tutor_response",
                "intent": tutor_response.intent,
                "next_actions": list(tutor_response.next_actions),
            },
        )
    if normalized_event_type == "quiz_answer" and audit_metadata.get("is_correct") is True:
        _complete_workspace_module(session, user=user, workspace=workspace)
    workspace.updated_at = datetime.now(UTC)
    session.add(event)
    if tutor_event is not None:
        session.add(tutor_event)
    session.commit()
    session.refresh(event)

    workspace = _load_workspace(session, user=user, workspace_id=workspace.id)
    assert workspace is not None
    return WorkspaceEventCreateResponse(
        event=event_to_schema(event),
        tutor_response=tutor_response,
        mastery_update=mastery_result.update,
        workspace=workspace_to_schema(session, workspace),
    )


def queue_workspace_video_generation(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID,
    generation_mode: str,
    template_id: str | None,
    spec_json: dict[str, Any],
    language: str,
    quality_profile: str,
    concept_id: UUID | None,
    metadata: dict[str, Any],
) -> WorkspaceGenerateVideoResponse | None:
    workspace = _load_workspace(session, user=user, workspace_id=workspace_id)
    if workspace is None:
        return None

    normalized_generation_mode = _normalize_generation_mode(generation_mode)
    if normalized_generation_mode == "context_auto":
        generated = generate_spec_from_workspace_context(
            workspace=workspace,
            language=language,
        )
        resolved_template_id = generated.template_id
        resolved_spec_json = generated.spec_json
        resolved_metadata = generated.debug_meta
    else:
        resolved_template_id = (template_id or "").strip().lower()
        if not resolved_template_id:
            raise ValueError("template_id must not be empty when generation_mode is 'manual'.")
        resolved_spec_json = dict(spec_json)
        resolved_metadata = {
            "spec_source": "manual_payload",
            "resolved_template_id": resolved_template_id,
        }

    queue = queue_animation_job(
        session,
        user=user,
        workspace_id=workspace.id,
        concept_id=concept_id,
        template_id=resolved_template_id,
        spec_json=resolved_spec_json,
        language=language,
        quality_profile=quality_profile,
    )
    event_metadata = {
        **metadata,
        "source": "workspace_generate_video_api",
        "generation_mode": normalized_generation_mode,
        "template_id": resolved_template_id,
        "job_id": str(queue.job_id),
        "artifact_id": str(queue.artifact_id),
        "queue_status": queue.status,
        **resolved_metadata,
    }
    if queue.error_details is not None:
        event_metadata["error_details"] = queue.error_details

    event = WorkspaceEvent(
        workspace_session_id=workspace.id,
        event_index=_next_event_index(session, workspace_id=workspace.id),
        event_type="media_generated",
        actor_type="system",
        text_payload="",
        image_asset_id=None,
        media_artifact_id=queue.artifact_id,
        input_event_id=None,
        metadata_json=event_metadata,
    )
    workspace.updated_at = datetime.now(UTC)
    session.add(event)
    session.commit()
    session.refresh(event)

    workspace = _load_workspace(session, user=user, workspace_id=workspace.id)
    if workspace is None:
        return None

    return WorkspaceGenerateVideoResponse(
        queue=queue,
        event=event_to_schema(event),
        workspace=workspace_to_schema(session, workspace),
    )


def workspace_to_schema(session: Session, workspace: WorkspaceSession) -> WorkspaceRead:
    events = sorted(
        workspace.events,
        key=lambda event: event.event_index,
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
        last_image_asset_id=_latest_image_asset_id(events),
        latest_media=media_artifact_to_schema(latest_media) if latest_media else None,
    )


def event_to_schema(event: WorkspaceEvent) -> WorkspaceEventRead:
    public_metadata = dict(event.metadata_json or {})
    public_metadata.pop("ai_audit", None)
    return WorkspaceEventRead(
        id=event.id,
        workspace_id=event.workspace_session_id,
        event_index=event.event_index,
        event_type=event.event_type,
        actor_type=event.actor_type,
        text_payload=event.text_payload,
        image_asset_id=event.image_asset_id,
        media_artifact_id=event.media_artifact_id,
        input_event_id=event.input_event_id,
        metadata=public_metadata,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )


def _workspace_session_summary(
    workspace: WorkspaceSession,
    *,
    fallback_title: str,
) -> WorkspaceSessionSummaryRead:
    events = sorted(workspace.events, key=lambda event: event.event_index)
    text_events = [
        event
        for event in events
        if event.text_payload.strip() and event.event_type in {"text", "quiz_answer", "note"}
    ]
    preview_event = text_events[-1] if text_events else None
    preview = preview_event.text_payload.strip() if preview_event else "Belum ada pesan."
    first_learner_event = next(
        (event for event in text_events if event.actor_type == "learner"),
        None,
    )
    title = first_learner_event.text_payload.strip() if first_learner_event else fallback_title
    if len(title) > 48:
        title = f"{title[:45].rstrip()}..."
    if len(preview) > 96:
        preview = f"{preview[:93].rstrip()}..."
    return WorkspaceSessionSummaryRead(
        id=workspace.id,
        track_id=workspace.track_id,
        module_id=workspace.module_id,
        title=title,
        preview=preview,
        message_count=len(text_events),
        created_at=workspace.created_at.isoformat() if workspace.created_at else "",
        updated_at=workspace.updated_at.isoformat() if workspace.updated_at else "",
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


def _next_event_index(session: Session, *, workspace_id: UUID) -> int:
    max_index = session.scalar(
        select(func.max(WorkspaceEvent.event_index)).where(
            WorkspaceEvent.workspace_session_id == workspace_id
        )
    )
    return int(max_index or 0) + 1


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


def _normalize_generation_mode(generation_mode: str) -> str:
    normalized = generation_mode.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"auto": "context_auto", "context": "context_auto"}
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"manual", "context_auto"}:
        raise ValueError("generation_mode must be either 'manual' or 'context_auto'.")
    return normalized


def _apply_workspace_pilot_context(workspace: WorkspaceSession) -> None:
    metadata = dict(workspace.metadata_json or {})
    metadata.update(
        {
            "active_node_id": _PILOT_NODE_ID,
            "active_concept_type": _PILOT_CONCEPT_TYPE,
            "active_template_id": _PILOT_TEMPLATE_ID,
            "active_prerequisites": list(_PILOT_PREREQUISITES),
            "context_source": _PILOT_CONTEXT_SOURCE,
        }
    )
    workspace.metadata_json = metadata


def _complete_workspace_module(
    session: Session,
    *,
    user: UserAccount,
    workspace: WorkspaceSession,
) -> None:
    track = session.scalar(
        select(LearningTrack)
        .where(LearningTrack.id == workspace.track_id, LearningTrack.user_id == user.id)
        .options(selectinload(LearningTrack.modules))
    )
    if track is None:
        return
    module = next((item for item in track.modules if item.id == workspace.module_id), None)
    if module is None:
        return

    module.status = "completed"
    modules = sorted(track.modules, key=lambda item: item.sort_order)
    completed_count = len([item for item in modules if item.status == "completed"])
    track.progress_percent = int(round((completed_count / max(1, len(modules))) * 100))
    next_module = next(
        (
            item
            for item in modules
            if item.sort_order > module.sort_order and item.status == "locked"
        ),
        None,
    )
    if next_module is not None:
        next_module.status = "ready"
    if completed_count == len(modules):
        track.status = "completed"
    else:
        track.status = "active"


# _deterministic_tutor_response removed: Gemini is now the primary tutor via tutor.py
# Fallback logic lives in app.modules.workspaces.tutor._fallback_response


def _latest_image_asset_id(events: list[WorkspaceEvent]) -> UUID | None:
    for event in reversed(events):
        if event.image_asset_id is not None:
            return event.image_asset_id
    return None


def _latest_media_artifact(
    session: Session,
    events: list[WorkspaceEvent],
) -> MediaArtifact | None:
    for event in reversed(events):
        if event.media_artifact_id is not None:
            return session.get(MediaArtifact, event.media_artifact_id)
    return None
