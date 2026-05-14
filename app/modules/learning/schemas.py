from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class LearningGoalCreateRequest(BaseModel):
    raw_topic: str = Field(..., min_length=2)
    subject_code: str | None = None


class AssessmentOptionRead(BaseModel):
    id: str
    label: str
    text: str


class AssessmentQuestionRead(BaseModel):
    id: str
    step_label: str
    topic: str
    prompt: str
    helper: str
    options: list[AssessmentOptionRead]


class LearningGoalCreateResponse(BaseModel):
    learning_goal_id: UUID
    status: str
    subject: str
    subject_code: str
    pretest_session_id: UUID
    track_id: UUID


class LearningGoalRead(BaseModel):
    id: UUID
    raw_topic: str
    normalized_topic: str
    status: str
    subject_code: str
    pretest_session_id: UUID | None = None
    track_id: UUID | None = None


class PretestReadResponse(BaseModel):
    session_id: UUID
    learning_goal_id: UUID
    title: str
    status: str
    questions: list[AssessmentQuestionRead]


class SubmitAnswerRequest(BaseModel):
    question_id: str
    option_id: str
    confidence: int = Field(default=0, ge=0, le=10)


class SubmitAnswerResponse(BaseModel):
    attempt_id: UUID
    accepted: bool = True
    is_correct: bool


class SubmitReasoningRequest(BaseModel):
    question_id: str
    option_id: str
    confidence: int = Field(default=0, ge=0, le=10)
    explanation: str = ""
    used_canvas: bool = False


class KnowledgeStateResponse(BaseModel):
    skill: str
    gap_label: str
    message: str
    path_title: str
    path_meta: str
    path_description: str


class TrackModuleRead(BaseModel):
    id: UUID
    title: str
    description: str
    estimated_minutes: int
    difficulty_label: str
    sort_order: int
    status: str


class TrackRead(BaseModel):
    id: UUID
    learning_goal_id: UUID
    title: str
    subtitle: str
    status: str
    progress_percent: int
    modules: list[TrackModuleRead] = Field(default_factory=list)


class TrackListResponse(BaseModel):
    items: list[TrackRead]


class DailyEvaluationResponse(BaseModel):
    session_id: UUID
    title: str
    status: str
    review_policy: dict[str, Any]
    questions: list[AssessmentQuestionRead]


class DailyEvaluationAnswerRequest(BaseModel):
    question_id: str
    option_id: str
    confidence: int = Field(default=0, ge=0, le=10)


class DailyEvaluationAnswerResponse(BaseModel):
    attempt_id: UUID
    is_correct: bool
    next_review_label: str
    mastery_delta: float
