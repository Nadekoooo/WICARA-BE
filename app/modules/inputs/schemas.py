from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class InputEventRead(BaseModel):
    id: UUID
    user_id: UUID
    event_type: str
    source_type: str
    text_payload: str
    image_asset_id: UUID | None = None
    workspace_session_id: UUID | None = None
    assessment_session_id: UUID | None = None
    concept_id: UUID | None = None
    selected_option_id: UUID | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    parsed_problem: dict[str, Any] = Field(default_factory=dict)
    parsed_work: dict[str, Any] = Field(default_factory=dict)
    confidence: int | None = None
    created_at: str
