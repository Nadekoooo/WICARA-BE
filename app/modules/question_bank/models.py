from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_dict_type = JSON().with_variant(JSONB, "postgresql")
json_list_type = JSON().with_variant(JSONB, "postgresql")


class QuestionBankItem(Base):
    __tablename__ = "question_bank_items"
    __table_args__ = (
        UniqueConstraint("external_id", name="uq_question_bank_items_external_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    subject_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL")
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="SET NULL")
    )
    subject_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    concept_code: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    concept_title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    education_level: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    grade_band: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en", index=True)
    assessment_types_json: Mapped[list[str]] = mapped_column(
        "assessment_types", json_list_type, nullable=False, default=list
    )
    question_type: Mapped[str] = mapped_column(String(64), nullable=False, default="multiple_choice")
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    cognitive_level: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    helper_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    answer_key: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    rubric_json: Mapped[dict[str, Any]] = mapped_column(
        "rubric", json_dict_type, nullable=False, default=dict
    )
    tags_json: Mapped[list[str]] = mapped_column(
        "tags", json_list_type, nullable=False, default=list
    )
    source_file: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    source_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    options: Mapped[list[QuestionBankOption]] = relationship(
        back_populates="item", cascade="all, delete-orphan", order_by="QuestionBankOption.sort_order"
    )


class QuestionBankOption(Base):
    __tablename__ = "question_bank_options"
    __table_args__ = (
        UniqueConstraint("question_bank_item_id", "option_key", name="uq_question_bank_options_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question_bank_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("question_bank_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    option_key: Mapped[str] = mapped_column(String(16), nullable=False)
    label: Mapped[str] = mapped_column(String(16), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    item: Mapped[QuestionBankItem] = relationship(back_populates="options")


class QuestionBankImportRun(Base):
    __tablename__ = "question_bank_import_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    imported_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    strict_mode: Mapped[bool] = mapped_column(nullable=False, default=False)
    errors_json: Mapped[list[dict[str, Any]]] = mapped_column(
        "errors", json_list_type, nullable=False, default=list
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
