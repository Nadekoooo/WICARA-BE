from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.learning.schemas import MediaArtifactRead


class WorkspaceCreateRequest(BaseModel):
    track_id: UUID
    module_id: UUID
    content_mode: str = Field(default="chat", min_length=2, max_length=32)


class WorkspaceEventCreateRequest(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=32)
    actor_type: str = Field(default="learner", min_length=2, max_length=32)
    text_payload: str = ""
    image_asset_id: UUID | None = None
    media_artifact_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkspaceEventRead(BaseModel):
    id: UUID
    workspace_id: UUID
    event_index: int
    event_type: str
    actor_type: str
    text_payload: str
    image_asset_id: UUID | None = None
    media_artifact_id: UUID | None = None
    input_event_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class WorkspaceRead(BaseModel):
    id: UUID
    track_id: UUID
    module_id: UUID
    current_topic: str
    content_mode: str
    status: str
    events: list[WorkspaceEventRead] = Field(default_factory=list)
    last_image_asset_id: UUID | None = None
    latest_media: MediaArtifactRead | None = None


class TutorResponseRead(BaseModel):
    text: str
    intent: str
    next_actions: list[str] = Field(default_factory=list)


class WorkspaceMasteryUpdateRead(BaseModel):
    concept_id: UUID | None = None
    mastery_score: float | None = None
    confidence_score: float | None = None
    evidence_count: int | None = None
    status: str | None = None
    delta: float = 0.0
    reason: str


class WorkspaceEventCreateResponse(BaseModel):
    event: WorkspaceEventRead
    tutor_response: TutorResponseRead | None = None
    mastery_update: WorkspaceMasteryUpdateRead | None = None
    workspace: WorkspaceRead
