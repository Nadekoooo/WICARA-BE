from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

json_dict_type = JSON().with_variant(JSONB, "postgresql")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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

    concepts: Mapped[list[KnowledgeConcept]] = relationship(
        back_populates="subject",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class KnowledgeConcept(Base):
    __tablename__ = "knowledge_concepts"
    __table_args__ = (
        UniqueConstraint("subject_id", "code", name="uq_knowledge_concepts_subject_code"),
        Index("ix_knowledge_concepts_subject_display_order", "subject_id", "display_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    grade_band: Mapped[str | None] = mapped_column(String(64))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    layout_x: Mapped[float | None] = mapped_column(Float)
    layout_y: Mapped[float | None] = mapped_column(Float)
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

    subject: Mapped[Subject] = relationship(back_populates="concepts")
    outgoing_edges: Mapped[list[ConceptEdge]] = relationship(
        back_populates="from_concept",
        cascade="all, delete-orphan",
        foreign_keys="ConceptEdge.from_concept_id",
        passive_deletes=True,
    )
    incoming_edges: Mapped[list[ConceptEdge]] = relationship(
        back_populates="to_concept",
        cascade="all, delete-orphan",
        foreign_keys="ConceptEdge.to_concept_id",
        passive_deletes=True,
    )


class ConceptEdge(Base):
    __tablename__ = "concept_edges"
    __table_args__ = (
        UniqueConstraint(
            "from_concept_id",
            "to_concept_id",
            "edge_type",
            name="uq_concept_edges_from_to_type",
        ),
        CheckConstraint("from_concept_id <> to_concept_id", name="ck_concept_edges_no_self_loop"),
        Index("ix_concept_edges_from_type", "from_concept_id", "edge_type"),
        Index("ix_concept_edges_to_type", "to_concept_id", "edge_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    from_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    to_concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("knowledge_concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    edge_type: Mapped[str] = mapped_column(String(32), nullable=False, default="prerequisite")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    from_concept: Mapped[KnowledgeConcept] = relationship(
        back_populates="outgoing_edges",
        foreign_keys=[from_concept_id],
    )
    to_concept: Mapped[KnowledgeConcept] = relationship(
        back_populates="incoming_edges",
        foreign_keys=[to_concept_id],
    )
