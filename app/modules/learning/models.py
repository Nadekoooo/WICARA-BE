from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
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


class LearningGoal(Base):
    __tablename__ = "learning_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("subjects.id"), nullable=False
    )
    target_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id")
    )
    raw_topic: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_topic: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pretest_ready")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    track: Mapped[LearningTrack | None] = relationship(back_populates="learning_goal")
    assessment_sessions: Mapped[list[AssessmentSession]] = relationship(
        back_populates="learning_goal", cascade="all, delete-orphan"
    )


class LearningTrack(Base):
    __tablename__ = "learning_tracks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    learning_goal_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("learning_goals.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pretest")
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    learning_goal: Mapped[LearningGoal] = relationship(back_populates="track")
    modules: Mapped[list[TrackModule]] = relationship(
        back_populates="track", cascade="all, delete-orphan", order_by="TrackModule.sort_order"
    )


class TrackModule(Base):
    __tablename__ = "track_modules"
    __table_args__ = (UniqueConstraint("track_id", "sort_order", name="uq_track_modules_order"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_tracks.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    difficulty_label: Mapped[str] = mapped_column(String(32), nullable=False, default="Medium")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="locked")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )

    track: Mapped[LearningTrack] = relationship(back_populates="modules")


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    learning_goal_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_goals.id", ondelete="CASCADE")
    )
    track_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_tracks.id", ondelete="SET NULL")
    )
    session_type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    learning_goal: Mapped[LearningGoal | None] = relationship(back_populates="assessment_sessions")
    questions: Mapped[list[AssessmentQuestion]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AssessmentQuestion.sort_order"
    )
    attempts: Mapped[list[AssessmentAttempt]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id")
    )
    step_label: Mapped[str] = mapped_column(String(64), nullable=False)
    topic: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    helper_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    difficulty_label: Mapped[str] = mapped_column(String(32), nullable=False, default="Medium")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )

    session: Mapped[AssessmentSession] = relationship(back_populates="questions")
    options: Mapped[list[AssessmentOption]] = relationship(
        back_populates="question", cascade="all, delete-orphan", order_by="AssessmentOption.sort_order"
    )


class AssessmentOption(Base):
    __tablename__ = "assessment_options"
    __table_args__ = (UniqueConstraint("question_id", "option_key", name="uq_assessment_options_key"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False
    )
    option_key: Mapped[str] = mapped_column(String(8), nullable=False)
    label: Mapped[str] = mapped_column(String(8), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    question: Mapped[AssessmentQuestion] = relationship(back_populates="options")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_questions.id", ondelete="CASCADE"), nullable=False
    )
    selected_option_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_options.id", ondelete="SET NULL")
    )
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    used_canvas: Mapped[bool] = mapped_column(nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evaluated_result: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped[AssessmentSession] = relationship(back_populates="attempts")


class LearnerConceptState(Base):
    __tablename__ = "learner_concept_states"
    __table_args__ = (
        UniqueConstraint("user_id", "concept_id", name="uq_learner_concept_states_user_concept"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
