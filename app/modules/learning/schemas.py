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
    track_id: UUID | None = None
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


class TrackModuleStateUpdateRequest(BaseModel):
    status: str = Field(..., min_length=2, max_length=32)


class TrackModuleStateUpdateResponse(BaseModel):
    track: TrackRead


class QueueItemRead(BaseModel):
    id: str
    track_id: UUID | None = None
    module_id: UUID | None = None
    title: str
    subtitle: str
    meta: str
    status: str
    estimated_minutes: int
    action_label: str


class LearningQueueResponse(BaseModel):
    recommended: list[QueueItemRead]
    tracks: list[TrackRead]


class DailySummaryRead(BaseModel):
    status: str
    title: str
    due_count: int
    completed_count: int


class HomeSummaryResponse(BaseModel):
    display_name: str
    first_name: str
    onboarding_completed: bool
    streak_days: int
    active_tracks_count: int
    next_queue_item: QueueItemRead | None = None
    daily_evaluation: DailySummaryRead
    active_tracks: list[TrackRead]


class MediaArtifactRead(BaseModel):
    id: UUID
    title: str
    subtitle: str
    artifact_type: str
    status: str
    duration_seconds: int
    duration_label: str
    thumbnail_url: str | None = None
    video_url: str | None = None
    playback_url: str | None = Field(
        default=None,
        description="Deprecated alias for video_url. Use video_url as source of truth.",
    )
    transcript: str
    notes: list[str]
    track_id: UUID | None = None
    module_id: UUID | None = None
    created_at: str


class MediaArtifactListResponse(BaseModel):
    items: list[MediaArtifactRead]


class MediaArtifactStatusResponse(BaseModel):
    artifact_id: UUID
    status: str
    progress: int
    error: str | None = None
    error_code: str | None = None
    error_details: dict[str, Any] | None = None


class AnimationQueueRequest(BaseModel):
    workspace_id: UUID | None = None
    concept_id: UUID | None = None
    template_id: str = Field(..., min_length=3, max_length=120)
    spec_json: dict[str, Any] = Field(default_factory=dict)
    language: str = Field(default="id", min_length=2, max_length=16)
    quality_profile: str = Field(default="standard", min_length=2, max_length=32)


class AnimationQueueResponse(BaseModel):
    job_id: UUID
    artifact_id: UUID
    status: str
    error_details: dict[str, Any] | None = None


class AnimationJobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    progress: int
    message: str
    artifact_id: UUID
    video_url: str | None = None
    thumbnail_url: str | None = None
    error: str | None = None
    error_details: dict[str, Any] | None = None


class ActionRead(BaseModel):
    label: str
    action_type: str
    target: str | None = None


class ProgressRead(BaseModel):
    current: int
    total: int
    completed: int
    label: str


class ReviewDueRead(BaseModel):
    title: str
    due_count: int
    summary: str
    action_label: str


class RetentionForecastPointRead(BaseModel):
    label: str
    retention_percent: int
    projected: bool = False


class RetentionForecastRead(BaseModel):
    title: str
    basis: str
    points: list[RetentionForecastPointRead]


class RecommendationCalloutRead(BaseModel):
    title: str
    message: str
    impact_label: str
    action_label: str


class ReportTrendRead(BaseModel):
    label: str
    before: float
    after: float


class ReportPerformanceGroupRead(BaseModel):
    label: str
    pre_test_percent: int
    post_test_percent: int


class GapMetricRead(BaseModel):
    count: int
    weekly_delta: int
    delta_label: str


class UnlockedConceptSummaryRead(BaseModel):
    count: int
    concepts: list[str]


class UpcomingRecommendationRead(BaseModel):
    title: str
    action_type: str
    reason: str
    due_date: str
    due_label: str


class ConsistencySummaryRead(BaseModel):
    title: str
    narrative: str
    signal: str


class WeeklyReportResponse(BaseModel):
    range_label: str
    range_start: str
    range_end: str
    status: str
    source: str
    score: int
    pretest_score_percent: int | None = None
    posttest_score_percent: int | None = None
    learning_gain_percent: int | None = None
    paired_concept_count: int = 0
    fixed_gaps: int
    fixed_gaps_delta: int
    remaining_gaps: int
    remaining_gaps_delta: int
    retention_minutes: int
    concepts: str
    summary_notes: list[str]
    trends: list[ReportTrendRead]
    performance_groups: list[ReportPerformanceGroupRead]
    gap_metrics: dict[str, GapMetricRead]
    unlocked_this_week: UnlockedConceptSummaryRead
    upcoming_recommendations: list[UpcomingRecommendationRead]
    consistency_summary: ConsistencySummaryRead


class DailyEvaluationResponse(BaseModel):
    session_id: UUID
    title: str
    status: str
    language: str
    source: str
    review_policy: dict[str, Any]
    review_due: ReviewDueRead
    progress: ProgressRead
    question: AssessmentQuestionRead | None = None
    questions: list[AssessmentQuestionRead]
    retention_forecast: RetentionForecastRead
    recommendation_callout: RecommendationCalloutRead


class DailyEvaluationAnswerRequest(BaseModel):
    question_id: str
    option_id: str
    confidence: int = Field(default=0, ge=0, le=10)


class DailyEvaluationAnswerResponse(BaseModel):
    attempt_id: UUID
    is_correct: bool
    next_review_label: str
    mastery_delta: float
    session_status: str
    completed: bool


class ReviewedConceptRead(BaseModel):
    concept_id: str | None = None
    title: str
    status_label: str
    mastery_score: float


class SpacedRepetitionImpactRead(BaseModel):
    retention_lift_percent: int
    days_until_next_review: int
    summary: str


class DailyEvaluationNextReviewRead(BaseModel):
    label: str
    due_date: str
    interval_days: int


class RecommendedNextActionRead(BaseModel):
    title: str
    action_type: str
    reason: str
    due_date: str | None = None
    priority: int


class DailyEvaluationResultResponse(BaseModel):
    session_id: UUID
    title: str
    status: str
    source: str
    score_percent: int
    reviewed_count: int
    correct_count: int
    review_again_count: int
    reviewed_concepts: list[ReviewedConceptRead]
    spaced_repetition_impact: SpacedRepetitionImpactRead
    next_review: DailyEvaluationNextReviewRead
    recommended_next_actions: list[RecommendedNextActionRead]
    back_to_home: ActionRead
