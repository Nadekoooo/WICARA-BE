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
    canvas_snapshot_id: UUID | None = None
    media_artifact_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkspaceEventRead(BaseModel):
    id: UUID
    workspace_id: UUID
    event_type: str
    actor_type: str
    text_payload: str
    canvas_snapshot_id: UUID | None = None
    media_artifact_id: UUID | None = None
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
    last_canvas_snapshot_id: UUID | None = None
    latest_media: MediaArtifactRead | None = None


class WorkspaceEventCreateResponse(BaseModel):
    event: WorkspaceEventRead
    tutor_response: WorkspaceEventRead | None = None
    workspace: WorkspaceRead
