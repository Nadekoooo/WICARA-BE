from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.accounts.models import UserAccount
from app.modules.inputs.models import InputEvent
from app.modules.inputs.schemas import InputEventRead


def create_workspace_input_event(
    session: Session,
    *,
    user: UserAccount,
    workspace_session_id: UUID,
    source_event_type: str,
    actor_type: str,
    text_payload: str,
    image_asset_id: UUID | None,
    media_artifact_id: UUID | None,
    metadata: dict[str, Any],
) -> InputEvent:
    event = InputEvent(
        user_id=user.id,
        workspace_session_id=workspace_session_id,
        event_type=_canonical_workspace_event_type(
            source_event_type=source_event_type,
            text_payload=text_payload,
            image_asset_id=image_asset_id,
        ),
        source_type="workspace",
        text_payload=text_payload.strip(),
        image_asset_id=image_asset_id,
        raw_payload={
            "source_event_type": source_event_type,
            "actor_type": actor_type,
            "text_payload": text_payload.strip(),
            "image_asset_id": str(image_asset_id) if image_asset_id else None,
            "media_artifact_id": str(media_artifact_id) if media_artifact_id else None,
            "metadata": metadata,
        },
        parsed_problem={},
        parsed_work={},
        confidence=_confidence_from_metadata(metadata),
    )
    session.add(event)
    session.flush()
    return event


def input_event_to_schema(event: InputEvent) -> InputEventRead:
    return InputEventRead(
        id=event.id,
        user_id=event.user_id,
        event_type=event.event_type,
        source_type=event.source_type,
        text_payload=event.text_payload,
        image_asset_id=event.image_asset_id,
        workspace_session_id=event.workspace_session_id,
        assessment_session_id=event.assessment_session_id,
        concept_id=event.concept_id,
        selected_option_id=event.selected_option_id,
        raw_payload=event.raw_payload or {},
        parsed_problem=event.parsed_problem or {},
        parsed_work=event.parsed_work or {},
        confidence=event.confidence,
        created_at=event.created_at.isoformat() if event.created_at else "",
    )


def _canonical_workspace_event_type(
    *,
    source_event_type: str,
    text_payload: str,
    image_asset_id: UUID | None,
) -> str:
    normalized = source_event_type.strip().lower().replace("-", "_").replace(" ", "_")
    has_text = bool(text_payload.strip())
    has_image = image_asset_id is not None
    if has_text and has_image:
        return "mixed"
    if normalized == "canvas_sent" or has_image:
        return "image"
    if normalized == "media_generated":
        return "media"
    if normalized == "quiz_answer":
        return "quiz_answer"
    if normalized in {"system", "note"}:
        return normalized
    return "text"


def _confidence_from_metadata(metadata: dict[str, Any]) -> int | None:
    value = metadata.get("confidence")
    if value is None:
        return None
    try:
        confidence = int(value)
    except (TypeError, ValueError):
        return None
    return max(0, min(10, confidence))
