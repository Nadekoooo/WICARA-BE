from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_dict_type = JSON().with_variant(JSONB, "postgresql")


class InputEvent(Base):
    __tablename__ = "input_events"
    __table_args__ = (
        Index("ix_input_events_user_created", "user_id", "created_at"),
        Index("ix_input_events_workspace_created", "workspace_session_id", "created_at"),
        Index("ix_input_events_assessment_created", "assessment_session_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace_session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspace_sessions.id", ondelete="CASCADE"),
    )
    assessment_session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessment_sessions.id", ondelete="CASCADE"),
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_concepts.id", ondelete="SET NULL"),
    )
    selected_option_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assessment_options.id", ondelete="SET NULL"),
    )
    image_asset_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    text_payload: Mapped[str] = mapped_column(Text, nullable=False, default="")
    raw_payload: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    parsed_problem: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    parsed_work: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    confidence: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
