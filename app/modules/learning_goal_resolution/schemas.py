from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ConceptCandidateRead(BaseModel):
    concept_id: UUID
    concept_code: str
    title: str
    description: str | None = None
    id_desc: str | None = None
    en_desc: str | None = None
    subject_code: str
    subject: str
    grade_band: str | None = None
    grade_relation: str | None = None
    level_note: str | None = None
    confidence: float | None = None
    aliases: list[str] = Field(default_factory=list)
    matched_signals: list[str] = Field(default_factory=list)


class ResolveLearningGoalRequest(BaseModel):
    raw_query: str = Field(..., min_length=2)
    subject_code: str | None = None
    education_level: str | None = None
    grade_level: str | None = None
    language: str | None = Field(default=None, min_length=2, max_length=16)


class ResolveLearningGoalResponse(BaseModel):
    resolution_id: UUID
    status: str
    suggested_concept: ConceptCandidateRead | None = None
    confidence: float
    alternatives: list[ConceptCandidateRead] = Field(default_factory=list)
    clarification_question: str | None = None
    search_scope: str = "subject_all_grades"
    search_scope_reason: str | None = None
    graph_focus: dict[str, Any] = Field(default_factory=dict)
    can_expand_scope: bool = False
    candidate_debug: list[dict[str, Any]] = Field(default_factory=list)


class ConfirmLearningGoalResponse(BaseModel):
    learning_goal_id: UUID
    status: str
    target_concept: ConceptCandidateRead


class RepromptLearningGoalRequest(BaseModel):
    raw_query: str = Field(..., min_length=2)


class SelectResolvedConceptRequest(BaseModel):
    concept_id: UUID | None = None
    concept_code: str | None = None


class ActiveGoalRead(BaseModel):
    id: UUID
    status: str
    raw_topic: str
    target_concept: ConceptCandidateRead | None = None
    pretest_session_id: UUID | None = None
    track_id: UUID | None = None
    next_action: str


class ActiveLearningGoalResponse(BaseModel):
    has_active_goal: bool
    goal: ActiveGoalRead | None = None
    active_goals: list[ActiveGoalRead] = Field(default_factory=list)


class ActiveLearningGoalConflict(BaseModel):
    error: str = "ACTIVE_LEARNING_GOAL_EXISTS"
    message: str = "You already have an active session goal for this node."
    active_goal: ActiveGoalRead


class CancelGoalResponse(BaseModel):
    learning_goal_id: UUID
    status: str
    abandoned_pretest_session_ids: list[UUID] = Field(default_factory=list)


class ArchiveGoalResponse(BaseModel):
    learning_goal_id: UUID
    status: str


class PathSelectionRequest(BaseModel):
    path_option: str


class PathModuleRead(BaseModel):
    id: UUID
    title: str
    description: str
    concept_code: str | None = None
    difficulty_label: str
    sort_order: int
    status: str


class PathSelectionResponse(BaseModel):
    track_id: UUID
    modules: list[PathModuleRead]
    goal_status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionGoalSummaryRead(BaseModel):
    learning_goal_id: UUID
    status: str
    raw_topic: str
    normalized_topic: str
    target_concept_id: UUID | None = None
    target_concept_code: str | None = None
    target_concept_title: str | None = None
    track_id: UUID | None = None
    workspace_session_id: UUID | None = None
    next_action: str
    created_at: str
    updated_at: str


class SubjectSessionGoalHistoryRead(BaseModel):
    subject_code: str
    subject_name: str
    session_goals: list[SessionGoalSummaryRead] = Field(default_factory=list)


class SessionGoalHistoryResponse(BaseModel):
    subjects: list[SubjectSessionGoalHistoryRead] = Field(default_factory=list)
