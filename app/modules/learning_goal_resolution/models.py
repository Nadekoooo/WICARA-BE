from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_dict_type = JSON().with_variant(JSONB, "postgresql")


class LearningGoalResolution(Base):
    __tablename__ = "learning_goal_resolutions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    education_level: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    grade_level: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    suggested_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="SET NULL")
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    alternatives_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    candidate_snapshot_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    llm_response_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    llm_model: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    prompt_version: Mapped[str] = mapped_column(
        String(64), nullable=False, default="goal_resolver_v2_multistage_lexical"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
