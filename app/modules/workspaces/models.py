from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_dict_type = JSON().with_variant(JSONB, "postgresql")


class WorkspaceSession(Base):
    __tablename__ = "workspace_sessions"
    __table_args__ = (
        Index("ix_workspace_sessions_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("user_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("learning_tracks.id", ondelete="CASCADE"),
        nullable=False,
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("track_modules.id", ondelete="CASCADE"),
        nullable=False,
    )
    current_topic: Mapped[str] = mapped_column(String(255), nullable=False)
    content_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="chat")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    events: Mapped[list[WorkspaceEvent]] = relationship(
        back_populates="workspace_session",
        cascade="all, delete-orphan",
        order_by="WorkspaceEvent.event_index",
    )


class WorkspaceEvent(Base):
    __tablename__ = "workspace_events"
    __table_args__ = (
        UniqueConstraint(
            "workspace_session_id",
            "event_index",
            name="uq_workspace_events_session_index",
        ),
        Index("ix_workspace_events_session_created", "workspace_session_id", "created_at"),
        Index("ix_workspace_events_session_index", "workspace_session_id", "event_index"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspace_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    event_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text_payload: Mapped[str] = mapped_column(Text, nullable=False, default="")
    image_asset_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    media_artifact_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_artifacts.id", ondelete="SET NULL"),
    )
    input_event_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("input_events.id", ondelete="SET NULL"),
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    workspace_session: Mapped[WorkspaceSession] = relationship(back_populates="events")
