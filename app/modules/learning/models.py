from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.curriculum.models import Subject

json_dict_type = JSON().with_variant(JSONB, "postgresql")


class LearningGoal(Base):
    __tablename__ = "learning_goals"
    __table_args__ = (
        Index(
            "uq_learning_goals_active_user_target",
            "user_id",
            "target_concept_id",
            unique=True,
            postgresql_where=text(
                "target_concept_id is not null and status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
            ),
            sqlite_where=text(
                "target_concept_id is not null and status in ('confirmed', 'pretest_in_progress', 'diagnosed', 'in_progress')"
            ),
        ),
    )

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
    resolution_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_goal_resolutions.id", ondelete="SET NULL")
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
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    track: Mapped[LearningTrack | None] = relationship(back_populates="learning_goal")
    subject: Mapped["Subject"] = relationship()
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
    target_concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="SET NULL")
    )
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="adaptive_generated")
    graph_scope_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    decision_state_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    max_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_nodes_visited: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    learning_goal: Mapped[LearningGoal | None] = relationship(back_populates="assessment_sessions")
    question_packs: Mapped[list[AssessmentQuestionPack]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    questions: Mapped[list[AssessmentQuestion]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AssessmentQuestion.sort_order"
    )
    attempts: Mapped[list[AssessmentAttempt]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class AssessmentQuestionPack(Base):
    __tablename__ = "assessment_question_packs"
    __table_args__ = (
        UniqueConstraint("session_id", "concept_id", name="uq_assessment_question_packs_session_concept"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_sessions.id", ondelete="CASCADE"), nullable=False
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="CASCADE"), nullable=False
    )
    generation_source: Mapped[str] = mapped_column(String(64), nullable=False, default="fallback_generated")
    llm_provider: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    llm_model: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False, default="adaptive_pack_v1")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped[AssessmentSession] = relationship(back_populates="question_packs")
    questions: Mapped[list[AssessmentQuestion]] = relationship(
        back_populates="pack", cascade="all, delete-orphan", order_by="AssessmentQuestion.sort_order"
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
    pack_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assessment_question_packs.id", ondelete="SET NULL")
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
    generation_source: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    generation_prompt_version: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    llm_metadata_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    expected_reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    rubric_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )

    session: Mapped[AssessmentSession] = relationship(back_populates="questions")
    pack: Mapped[AssessmentQuestionPack | None] = relationship(back_populates="questions")
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
    canvas_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("image_assets.id", ondelete="SET NULL")
    )
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    typed_reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")
    used_canvas: Mapped[bool] = mapped_column(nullable=False, default=False)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_correct: Mapped[bool] = mapped_column(nullable=False, default=False)
    answer_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning_score: Mapped[float | None] = mapped_column(Float)
    canvas_score: Mapped[float | None] = mapped_column(Float)
    evidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    diagnostic_signal: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    evaluated_result: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    evaluation_metadata_json: Mapped[dict[str, Any]] = mapped_column(
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


class WeeklyReportSnapshot(Base):
    __tablename__ = "weekly_report_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "range_start",
            "range_end",
            name="uq_weekly_report_snapshots_user_range",
        ),
        Index("ix_weekly_report_snapshots_user_start", "user_id", "range_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    range_start: Mapped[date] = mapped_column(Date, nullable=False)
    range_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="seeded_baseline")
    source: Mapped[str] = mapped_column(String(96), nullable=False, default="seeded_mvp")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fixed_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    remaining_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overdue_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_gaps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    paired_concept_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payload_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class MediaArtifact(Base):
    __tablename__ = "media_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False
    )
    track_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_tracks.id", ondelete="SET NULL")
    )
    module_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("track_modules.id", ondelete="SET NULL")
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("workspace_sessions.id", ondelete="SET NULL")
    )
    concept_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("knowledge_concepts.id", ondelete="SET NULL")
    )
    template_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    spec_json: Mapped[dict[str, Any]] = mapped_column(json_dict_type, nullable=False, default=dict)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    quality_profile: Mapped[str] = mapped_column(String(32), nullable=False, default="standard")
    artifact_type: Mapped[str] = mapped_column(String(32), nullable=False, default="video")
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ready")
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    thumbnail_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    playback_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    video_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    transcript: Mapped[str] = mapped_column(Text, nullable=False, default="")
    notes_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", json_dict_type, nullable=False, default=dict
    )
    render_meta_json: Mapped[dict[str, Any]] = mapped_column(
        json_dict_type, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    jobs: Mapped[list[MediaJob]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )


class MediaJob(Base):
    __tablename__ = "media_jobs"
    __table_args__ = (
        Index("ix_media_jobs_status_created", "status", "created_at"),
        Index("ix_media_jobs_artifact_id", "artifact_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("media_artifacts.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    artifact: Mapped[MediaArtifact] = relationship(back_populates="jobs")
