from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.modules.accounts.models import UserAccount
from app.modules.curriculum.kurikulum_merdeka import canonical_subject_code
from app.modules.curriculum.models import KnowledgeConcept, Subject
from app.modules.curriculum.seed import seed_curriculum
from app.modules.learning.job_queue import build_media_job_queue_adapter
from app.modules.learning.models import (
    AssessmentAttempt,
    AssessmentOption,
    AssessmentQuestion,
    AssessmentSession,
    LearnerConceptState,
    LearningGoal,
    LearningTrack,
    MediaArtifact,
    MediaJob,
    TrackModule,
)
from app.modules.learning.schemas import (
    AnimationJobStatusResponse,
    AnimationQueueResponse,
    ActionRead,
    AssessmentOptionRead,
    AssessmentQuestionRead,
    DailyEvaluationAnswerResponse,
    DailyEvaluationNextReviewRead,
    DailyEvaluationResponse,
    DailyEvaluationResultResponse,
    DailySummaryRead,
    GapMetricRead,
    HomeSummaryResponse,
    KnowledgeStateResponse,
    LearningQueueResponse,
    LearningGoalCreateResponse,
    LearningGoalRead,
    MediaArtifactListResponse,
    MediaArtifactRead,
    MediaArtifactStatusResponse,
    PretestReadResponse,
    QueueItemRead,
    RecommendationCalloutRead,
    RecommendedNextActionRead,
    ReportTrendRead,
    ReportPerformanceGroupRead,
    RetentionForecastPointRead,
    RetentionForecastRead,
    ReviewDueRead,
    ReviewedConceptRead,
    SpacedRepetitionImpactRead,
    SubmitAnswerResponse,
    TrackListResponse,
    TrackModuleRead,
    TrackModuleStateUpdateResponse,
    TrackRead,
    UnlockedConceptSummaryRead,
    UpcomingRecommendationRead,
    ConsistencySummaryRead,
    WeeklyReportResponse,
    ProgressRead,
)
from app.modules.learning.render_engine import (
    RenderEngineError,
    RenderOutput,
    render_template_scene,
)
from app.modules.learning.template_validation import (
    TemplateValidationError,
    validate_template_spec,
)
from app.modules.workspaces.models import WorkspaceSession

logger = logging.getLogger(__name__)


PRETEST_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Prerequisite probe",
        "prompt": (
            "A student wants to learn derivatives, but their graph approaches y = 3 "
            "as x gets closer to 2 from both sides. What should WICARA check first?"
        ),
        "helper": "Choose the prerequisite signal that best guides the first learning path.",
        "concept_hints": ["intuitive_limits", "limit", "bilangan_rasional"],
        "correct": "B",
        "options": [
            ("A", "Start derivative rules immediately"),
            ("B", "Check whether the learner understands limits from graphs"),
            ("C", "Skip prerequisite diagnosis and generate a video"),
            ("D", "Mark calculus as mastered from one topic request"),
        ],
    },
    {
        "topic": "Learning path diagnosis",
        "prompt": (
            "A learner can apply a formula after seeing it, but cannot explain why "
            "the formula works. What should the adaptive track do next?"
        ),
        "helper": "Pick the action that keeps the path prerequisite-first.",
        "concept_hints": ["functions", "bilangan_bulat"],
        "correct": "C",
        "options": [
            ("A", "Increase difficulty because the formula was copied correctly"),
            ("B", "Skip explanation and only give more multiple-choice questions"),
            ("C", "Add a short concept-building module before harder practice"),
            ("D", "Remove the concept from the learning map"),
        ],
    },
]


DAILY_REVIEW_TEMPLATES: list[dict[str, Any]] = [
    {
        "topic": "Spaced review",
        "prompt": (
            "You answered a concept correctly today after struggling yesterday. "
            "What is the best next step?"
        ),
        "helper": "Use memory strength to decide.",
        "concept_hints": ["bilangan_rasional", "intuitive_limits"],
        "correct": "A",
        "options": [
            ("A", "Review it again after a short delay"),
            ("B", "Mark it mastered forever immediately"),
            ("C", "Remove it from all future practice"),
            ("D", "Only study brand new concepts now"),
        ],
    },
    {
        "topic": "Application",
        "prompt": (
            "A student can solve derivative rules but misses word problems. "
            "What should they review next?"
        ),
        "helper": "Pick the next learning action.",
        "concept_hints": ["applications_derivatives", "functions", "bilangan_bulat"],
        "correct": "B",
        "options": [
            ("A", "Repeat only memorized derivative formulas"),
            ("B", "Practice translating situations into equations"),
            ("C", "Skip application questions until later"),
            ("D", "Review unrelated facts without checking the gap"),
        ],
    },
    {
        "topic": "Concept decay",
        "prompt": (
            "A learner mastered a prerequisite last week, but confidence is dropping. "
            "How should WICARA schedule it?"
        ),
        "helper": "Choose the retention-oriented action.",
        "concept_hints": ["functions", "bilangan_rasional"],
        "correct": "D",
        "options": [
            ("A", "Ignore it because it was once mastered"),
            ("B", "Reset the full track to the beginning"),
            ("C", "Only show new concepts today"),
            ("D", "Add a short review question before the next module"),
        ],
    },
]

MEDIA_JOB_PROGRESS_STAGES: list[tuple[int, str]] = [
    (20, "Validating render payload."),
    (45, "Preparing template rendering inputs."),
]


def create_learning_goal(
    session: Session,
    *,
    user: UserAccount,
    raw_topic: str,
    subject_code: str | None,
) -> LearningGoalCreateResponse:
    ensure_curriculum_seeded(session)
    subject = _resolve_subject(session, subject_code=subject_code, user=user)
    concept = _pick_concept(session, subject=subject, raw_topic=raw_topic)

    normalized_topic = _normalize_topic(raw_topic)
    goal = LearningGoal(
        user_id=user.id,
        subject_id=subject.id,
        target_concept_id=concept.id if concept else None,
        raw_topic=raw_topic.strip(),
        normalized_topic=normalized_topic,
        status="pretest_ready",
        metadata_json={"source": "learning_goal_api", "generation": "deterministic_seed"},
    )
    session.add(goal)
    session.flush()

    track = _create_track(session, user=user, goal=goal, subject=subject, concept=concept)
    pretest = _create_assessment_session(
        session,
        user=user,
        learning_goal=goal,
        track=track,
        session_type="pretest",
        title=f"Pretest for {normalized_topic}",
        templates=PRETEST_TEMPLATES,
    )
    session.commit()

    return LearningGoalCreateResponse(
        learning_goal_id=goal.id,
        status=goal.status,
        subject=subject.name,
        subject_code=subject.code,
        pretest_session_id=pretest.id,
        track_id=track.id,
    )


def read_learning_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID,
) -> LearningGoalRead | None:
    goal = session.scalar(
        select(LearningGoal)
        .where(LearningGoal.id == learning_goal_id, LearningGoal.user_id == user.id)
        .options(selectinload(LearningGoal.track), selectinload(LearningGoal.assessment_sessions))
    )
    if goal is None:
        return None
    subject = session.get(Subject, goal.subject_id)
    pretest = next(
        (item for item in goal.assessment_sessions if item.session_type == "pretest"),
        None,
    )
    return LearningGoalRead(
        id=goal.id,
        raw_topic=goal.raw_topic,
        normalized_topic=goal.normalized_topic,
        status=goal.status,
        subject_code=subject.code if subject else "",
        pretest_session_id=pretest.id if pretest else None,
        track_id=goal.track.id if goal.track else None,
    )


def get_pretest_for_goal(
    session: Session,
    *,
    user: UserAccount,
    learning_goal_id: UUID,
) -> PretestReadResponse | None:
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.learning_goal_id == learning_goal_id,
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "pretest",
        )
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        return None
    return PretestReadResponse(
        session_id=assessment.id,
        learning_goal_id=learning_goal_id,
        title=assessment.title,
        status=assessment.status,
        questions=[question_to_schema(question) for question in assessment.questions],
    )


def submit_answer(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
    explanation: str = "",
    used_canvas: bool = False,
) -> tuple[AssessmentAttempt, bool]:
    assessment, question, option = _resolve_submission_targets(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
    )
    attempt = AssessmentAttempt(
        session_id=assessment.id,
        question_id=question.id,
        selected_option_id=option.id,
        confidence=confidence,
        explanation_text=explanation.strip(),
        used_canvas=used_canvas,
        score=1.0 if option.is_correct else 0.0,
        evaluated_result={
            "verdict": "CORRECT" if option.is_correct else "INCORRECT",
            "grading": "deterministic_seed",
        },
    )
    session.add(attempt)
    _update_mastery(session, user=user, question=question, is_correct=option.is_correct)
    session.commit()
    session.refresh(attempt)
    return attempt, option.is_correct


def submit_answer_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
) -> SubmitAnswerResponse:
    attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
    )
    return SubmitAnswerResponse(attempt_id=attempt.id, is_correct=is_correct)


def submit_reasoning_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
    explanation: str,
    used_canvas: bool,
) -> KnowledgeStateResponse:
    _attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
        explanation=explanation,
        used_canvas=used_canvas,
    )
    assessment = session.get(AssessmentSession, assessment_session_id)
    if assessment:
        assessment.status = "completed"
        assessment.completed_at = datetime.now(UTC)
        if assessment.learning_goal_id:
            goal = session.get(LearningGoal, assessment.learning_goal_id)
            if goal:
                goal.status = "track_ready"
        if assessment.track_id:
            track = session.get(LearningTrack, assessment.track_id)
            if track:
                track.status = "active"
                track.progress_percent = 8
        session.commit()

    if is_correct:
        return KnowledgeStateResponse(
            skill="Ready concept: prerequisite reading",
            gap_label="READY",
            message=(
                "Your pretest evidence is enough to start the generated path. "
                "WICARA will still keep early prerequisites in review."
            ),
            path_title="Personalized path generated",
            path_meta="20-28 min | 3 modules",
            path_description="Start with the detected prerequisite, then move into the requested topic.",
        )
    return KnowledgeStateResponse(
        skill="Missing prerequisite: concept diagnosis",
        gap_label="GAP",
        message=(
            "The gap looks like jumping to the target topic before confirming the "
            "prerequisite signal. The path will repair that first."
        ),
        path_title="Prerequisite-first path generated",
        path_meta="18-24 min | 3 modules",
        path_description="Review the missing foundation, then return to your original learning goal.",
    )


def list_tracks(session: Session, *, user: UserAccount) -> TrackListResponse:
    tracks = list(
        session.scalars(
            select(LearningTrack)
            .where(LearningTrack.user_id == user.id)
            .options(selectinload(LearningTrack.modules))
            .order_by(LearningTrack.created_at.desc())
        )
    )
    return TrackListResponse(items=[track_to_schema(track) for track in tracks])


def get_home_summary(session: Session, *, user: UserAccount) -> HomeSummaryResponse:
    tracks = _user_tracks(session, user=user)
    queue = _build_queue_items(tracks)
    daily_session = _today_daily_session(session, user=user)
    completed_today = 0
    if daily_session is not None:
        completed_today = session.scalar(
            select(func.count(AssessmentAttempt.id)).where(
                AssessmentAttempt.session_id == daily_session.id
            )
        ) or 0
    display_name = _display_name_for_user(user)
    return HomeSummaryResponse(
        display_name=display_name,
        first_name=_first_name(display_name),
        onboarding_completed=bool(user.learner_profile and user.learner_profile.onboarding_completed),
        streak_days=_streak_days(session, user=user),
        active_tracks_count=len([track for track in tracks if track.status != "completed"]),
        next_queue_item=queue[0] if queue else None,
        daily_evaluation=DailySummaryRead(
            status="completed" if completed_today else "ready",
            title="Daily Evaluation",
            due_count=max(0, 3 - completed_today),
            completed_count=completed_today,
        ),
        active_tracks=[track_to_schema(track) for track in tracks[:3]],
    )


def get_learning_queue(session: Session, *, user: UserAccount) -> LearningQueueResponse:
    tracks = _user_tracks(session, user=user)
    return LearningQueueResponse(
        recommended=_build_queue_items(tracks),
        tracks=[track_to_schema(track) for track in tracks],
    )


def get_track_modules(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
) -> TrackRead | None:
    track = session.scalar(
        select(LearningTrack)
        .where(LearningTrack.id == track_id, LearningTrack.user_id == user.id)
        .options(selectinload(LearningTrack.modules))
    )
    return track_to_schema(track) if track is not None else None


def update_track_module_state(
    session: Session,
    *,
    user: UserAccount,
    track_id: UUID,
    module_id: UUID,
    status: str,
) -> TrackModuleStateUpdateResponse | None:
    normalized_status = status.strip().lower()
    if normalized_status not in {"locked", "ready", "active", "completed"}:
        raise ValueError("Module status must be locked, ready, active, or completed.")
    track = session.scalar(
        select(LearningTrack)
        .where(LearningTrack.id == track_id, LearningTrack.user_id == user.id)
        .options(selectinload(LearningTrack.modules))
    )
    if track is None:
        return None
    module = next((item for item in track.modules if item.id == module_id), None)
    if module is None:
        return None
    module.status = normalized_status
    if normalized_status == "active":
        track.status = "active"
    if normalized_status == "completed":
        modules = sorted(track.modules, key=lambda item: item.sort_order)
        completed_count = len([item for item in modules if item.status == "completed"])
        track.progress_percent = int(round((completed_count / max(1, len(modules))) * 100))
        next_module = next(
            (item for item in modules if item.sort_order > module.sort_order and item.status == "locked"),
            None,
        )
        if next_module is not None:
            next_module.status = "ready"
        if completed_count == len(modules):
            track.status = "completed"
    session.commit()
    session.refresh(track)
    return TrackModuleStateUpdateResponse(track=track_to_schema(track))


def queue_animation_job(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID | None,
    concept_id: UUID | None,
    template_id: str,
    spec_json: dict[str, Any],
    language: str,
    quality_profile: str,
) -> AnimationQueueResponse:
    normalized_template_id = template_id.strip().lower()
    if not normalized_template_id:
        raise ValueError("template_id must not be empty.")

    workspace = _resolve_owned_workspace(session, user=user, workspace_id=workspace_id)
    resolved_concept_id = _resolve_concept_id(
        session,
        concept_id=concept_id,
        workspace=workspace,
    )
    normalized_language = _normalize_short_label(language, fallback="id", max_length=16)
    normalized_quality = _normalize_short_label(
        quality_profile, fallback="standard", max_length=32
    )
    validation_result = None
    validation_error: TemplateValidationError | None = None
    try:
        validation_result = validate_template_spec(
            template_id=normalized_template_id,
            spec_json=spec_json,
        )
    except TemplateValidationError as exc:
        validation_error = exc

    canonical_template_id = (
        validation_result.template_id
        if validation_result is not None
        else (validation_error.template_id or normalized_template_id)
    )
    normalized_spec = (
        validation_result.normalized_spec
        if validation_result is not None
        else dict(spec_json)
    )
    job_status = "queued" if validation_error is None else "failed"
    job_message = (
        "Job is queued for rendering."
        if validation_error is None
        else "Template validation failed."
    )
    error_details = validation_error.to_dict() if validation_error is not None else None
    artifact = MediaArtifact(
        user_id=user.id,
        track_id=workspace.track_id if workspace else None,
        module_id=workspace.module_id if workspace else None,
        workspace_id=workspace.id if workspace else None,
        concept_id=resolved_concept_id,
        template_id=canonical_template_id,
        spec_json=normalized_spec,
        language=normalized_language,
        quality_profile=normalized_quality,
        artifact_type="video",
        title=_queued_artifact_title(normalized_spec, canonical_template_id),
        subtitle=_queued_artifact_subtitle(normalized_spec),
        status=job_status,
        duration_seconds=0,
        thumbnail_url="",
        playback_url="",
        video_url="",
        transcript="",
        notes_json=[],
        metadata_json={
            "source": "animation_queue_api",
            "progress": 0,
            "job_state": job_status,
        },
        render_meta_json=_initial_render_meta(
            validation_result=validation_result,
            validation_error=error_details,
        ),
    )
    session.add(artifact)
    session.flush()

    job = MediaJob(
        artifact_id=artifact.id,
        status=job_status,
        progress=0,
        message=job_message,
        attempt=0,
        error=validation_error.message if validation_error is not None else None,
    )
    session.add(job)
    _sync_artifact_job_state(
        artifact=artifact,
        job=job,
        error_message=validation_error.message if validation_error is not None else None,
        error_details=error_details,
        error_code=validation_error.code if validation_error is not None else None,
    )
    session.commit()
    session.refresh(job)
    if validation_error is None:
        published = _publish_media_job_to_queue(job_id=job.id)
        if not published:
            job.message = "Job queued in database. Waiting for worker polling fallback."
            session.commit()
    return AnimationQueueResponse(
        job_id=job.id,
        artifact_id=artifact.id,
        status=job.status,
        error_details=error_details,
    )


def get_animation_job_status(
    session: Session,
    *,
    user: UserAccount,
    job_id: UUID,
) -> AnimationJobStatusResponse | None:
    row = session.execute(
        select(MediaJob, MediaArtifact)
        .join(MediaArtifact, MediaArtifact.id == MediaJob.artifact_id)
        .where(
            MediaJob.id == job_id,
            MediaArtifact.user_id == user.id,
        )
    ).first()
    if row is None:
        return None

    job, artifact = row
    video_url = artifact.video_url or artifact.playback_url
    error_details = artifact.render_meta_json.get("error_details")
    return AnimationJobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=max(0, min(100, int(job.progress or 0))),
        message=job.message or "",
        artifact_id=artifact.id,
        video_url=video_url,
        thumbnail_url=artifact.thumbnail_url,
        error=job.error,
        error_details=error_details if isinstance(error_details, dict) else None,
    )


def pick_next_queued_animation_job_id(session: Session) -> UUID | None:
    return session.scalar(
        select(MediaJob.id).where(MediaJob.status == "queued").order_by(MediaJob.created_at).limit(1)
    )


def process_animation_job_for_worker(
    session: Session,
    *,
    job_id: UUID,
) -> bool:
    row = _load_job_with_artifact(session, job_id=job_id)
    if row is None:
        logger.warning("Media worker received unknown job id %s.", job_id)
        return False
    job, artifact = row
    if job.status in {"ready", "failed"}:
        return True

    try:
        settings = get_settings()
        _mark_job_processing(session, job=job, artifact=artifact)
        _validate_job_payload(session=session, job=job, artifact=artifact)
        for progress, message in MEDIA_JOB_PROGRESS_STAGES:
            _update_job_progress(
                session,
                job=job,
                artifact=artifact,
                progress=progress,
                message=message,
            )
        render_output, attempts_used = _render_artifact_with_retry(
            session,
            job=job,
            artifact=artifact,
            max_attempts=settings.media_render_max_attempts,
            timeout_seconds=settings.media_render_timeout_seconds,
        )
        _attach_render_output_to_artifact(
            session,
            artifact=artifact,
            render_output=render_output,
            attempts_used=attempts_used,
        )
        _update_job_progress(
            session,
            job=job,
            artifact=artifact,
            progress=90,
            message="Render output stored in local artifact path.",
        )
        _mark_job_ready(
            session,
            job=job,
            artifact=artifact,
            final_message="Render lifecycle finished. Artifact is ready.",
        )
        return True
    except TemplateValidationError as exc:
        _mark_job_failed(
            session,
            job=job,
            artifact=artifact,
            error_message=exc.message,
            error_code=exc.code,
            error_details=exc.to_dict(),
        )
        return False
    except RenderEngineError as exc:
        _mark_job_failed(
            session,
            job=job,
            artifact=artifact,
            error_message=exc.message,
            error_code=exc.code,
            error_details=exc.to_dict(),
        )
        return False
    except Exception as exc:
        _mark_job_failed(
            session,
            job=job,
            artifact=artifact,
            error_message=str(exc),
        )
        return False


def list_media_artifacts(session: Session, *, user: UserAccount) -> MediaArtifactListResponse:
    _ensure_sample_media_artifacts(session, user=user)
    artifacts = list(
        session.scalars(
            select(MediaArtifact)
            .where(MediaArtifact.user_id == user.id)
            .order_by(MediaArtifact.created_at.desc(), MediaArtifact.title)
        )
    )
    return MediaArtifactListResponse(items=[media_artifact_to_schema(item) for item in artifacts])


def get_media_artifact(
    session: Session,
    *,
    user: UserAccount,
    artifact_id: UUID,
) -> MediaArtifactRead | None:
    _ensure_sample_media_artifacts(session, user=user)
    artifact = session.scalar(
        select(MediaArtifact).where(
            MediaArtifact.id == artifact_id,
            MediaArtifact.user_id == user.id,
        )
    )
    return media_artifact_to_schema(artifact) if artifact else None


def get_media_artifact_status(
    session: Session,
    *,
    user: UserAccount,
    artifact_id: UUID,
) -> MediaArtifactStatusResponse | None:
    _ensure_sample_media_artifacts(session, user=user)
    artifact = session.scalar(
        select(MediaArtifact).where(
            MediaArtifact.id == artifact_id,
            MediaArtifact.user_id == user.id,
        )
    )
    if artifact is None:
        return None
    progress = artifact.metadata_json.get("progress")
    return MediaArtifactStatusResponse(
        artifact_id=artifact.id,
        status=artifact.status,
        progress=int(progress) if isinstance(progress, int) else (100 if artifact.status == "ready" else 0),
        error=str(artifact.metadata_json.get("error")) if artifact.metadata_json.get("error") else None,
    )


def get_latest_weekly_report(session: Session, *, user: UserAccount) -> WeeklyReportResponse:
    week_start, week_end = _current_week_range()
    return get_weekly_report(session, user=user, start=week_start, end=week_end)


def get_weekly_report(
    session: Session,
    *,
    user: UserAccount,
    start: date,
    end: date,
) -> WeeklyReportResponse:
    start_at, end_at = _date_range_bounds(start, end)
    range_attempts = _assessment_attempt_rows(
        session,
        user=user,
        submitted_from=start_at,
        submitted_before=end_at,
    )
    baseline_attempts = _assessment_attempt_rows(
        session,
        user=user,
        submitted_before=start_at,
    )
    attempts_count = len(range_attempts)
    states = list(
        session.scalars(select(LearnerConceptState).where(LearnerConceptState.user_id == user.id))
    )
    mastered_or_ready = len([state for state in states if state.status in {"mastered", "ready"}])
    review_due = len([state for state in states if state.status in {"review_due", "gap"}])
    fixed_in_range = len(
        [
            state
            for state in states
            if state.status in {"mastered", "ready"}
            and state.last_evaluated_at is not None
            and start_at <= _as_utc(state.last_evaluated_at) < end_at
        ]
    )
    score = _attempt_correct_percent(range_attempts) if range_attempts else 72
    fixed_gaps = fixed_in_range if fixed_in_range else (mastered_or_ready if states else 3)
    remaining_gaps = review_due if states else 2
    retention_minutes = int(sum(state.evidence_count for state in states) * 6) if states else 18
    concept_names = _recent_concept_names(session, user=user)
    trends = _report_trends(range_attempts=range_attempts, baseline_attempts=baseline_attempts)
    fixed_delta = fixed_in_range if attempts_count or states else 4
    remaining_delta = -max(1, min(3, remaining_gaps)) if attempts_count else -2
    unlocked_count = max(1, min(8, mastered_or_ready or len(concept_names) or 3))
    unlocked_concepts = concept_names[:unlocked_count] or [
        "Limits from graphs",
        "Derivative intuition",
        "Application translation",
    ]
    recommendations = _weekly_recommendations(
        session=session,
        user=user,
        states=states,
        remaining_gaps=remaining_gaps,
        week_end=end,
    )
    has_baseline = bool(baseline_attempts)
    status = "complete" if attempts_count else "seeded_baseline"
    if attempts_count and has_baseline:
        source = "derived_from_range_assessments_and_mastery"
    elif attempts_count:
        source = "derived_from_range_assessments_no_baseline"
    elif states:
        source = "derived_from_mastery_state"
    else:
        source = "seeded_mvp"
    return WeeklyReportResponse(
        range_label=_format_week_label(start, end),
        range_start=start.isoformat(),
        range_end=end.isoformat(),
        status=status,
        source=source,
        score=score,
        fixed_gaps=fixed_gaps,
        fixed_gaps_delta=fixed_delta,
        remaining_gaps=remaining_gaps,
        remaining_gaps_delta=remaining_delta,
        retention_minutes=retention_minutes,
        concepts=", ".join(concept_names) if concept_names else "Limits, graph reading",
        summary_notes=[
            "Report is aggregated from persisted attempts submitted inside the selected date range.",
            "Gap deltas are inferred from current mastery because historical state snapshots are not yet stored.",
        ],
        trends=trends,
        performance_groups=[
            ReportPerformanceGroupRead(
                label=trend.label,
                pre_test_percent=round(trend.before * 100),
                post_test_percent=round(trend.after * 100),
            )
            for trend in trends
        ],
        gap_metrics={
            "fixed": GapMetricRead(
                count=fixed_gaps,
                weekly_delta=fixed_delta,
                delta_label=f"+{fixed_delta} this week",
            ),
            "remaining": GapMetricRead(
                count=remaining_gaps,
                weekly_delta=remaining_delta,
                delta_label=f"{remaining_delta} this week",
            ),
        },
        unlocked_this_week=UnlockedConceptSummaryRead(
            count=unlocked_count,
            concepts=unlocked_concepts,
        ),
        upcoming_recommendations=recommendations,
        consistency_summary=ConsistencySummaryRead(
            title="Consistency is compounding.",
            narrative="Keep it up - your future self will thank you.",
            signal="daily_review_and_gap_closure",
        ),
    )


def get_or_create_daily_evaluation(
    session: Session,
    *,
    user: UserAccount,
) -> DailyEvaluationResponse:
    ensure_curriculum_seeded(session)
    today = datetime.now(UTC).date().isoformat()
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "daily_evaluation",
            AssessmentSession.metadata_json["review_date"].as_string() == today,
        )
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        assessment = _create_assessment_session(
            session,
            user=user,
            learning_goal=None,
            track=None,
            session_type="daily_evaluation",
            title="Daily Evaluation",
            templates=DAILY_REVIEW_TEMPLATES,
            metadata={"review_date": today, "policy": "spaced_repetition_mvp"},
        )
        session.commit()
        assessment = session.scalar(
            select(AssessmentSession)
            .where(AssessmentSession.id == assessment.id)
            .options(
                selectinload(AssessmentSession.questions).selectinload(
                    AssessmentQuestion.options
                )
            )
        )
    assert assessment is not None
    completed_question_ids = _answered_question_ids(session, assessment_id=assessment.id)
    questions = [question_to_schema(question) for question in assessment.questions]
    total_questions = len(questions)
    completed_count = len(completed_question_ids)
    current_question = next(
        (question for question in assessment.questions if question.id not in completed_question_ids),
        assessment.questions[0] if assessment.questions else None,
    )
    due_count = max(0, total_questions - completed_count)
    return DailyEvaluationResponse(
        session_id=assessment.id,
        title=assessment.title,
        status=assessment.status,
        language=_language_for_user(user),
        source=_daily_source(assessment),
        review_policy={
            "strategy": "spaced_repetition_mvp",
            "basis": "due concepts first, seeded review templates when no due concepts exist",
        },
        review_due=ReviewDueRead(
            title="Review due",
            due_count=due_count,
            summary=f"{due_count} items ready for review",
            action_label="Start" if completed_count == 0 else "Continue",
        ),
        progress=ProgressRead(
            current=min(total_questions, completed_count + 1) if total_questions else 0,
            total=total_questions,
            completed=completed_count,
            label=(
                f"{min(total_questions, completed_count + 1)} of {total_questions}"
                if total_questions
                else "0 of 0"
            ),
        ),
        question=question_to_schema(current_question) if current_question else None,
        questions=questions,
        retention_forecast=_retention_forecast(completed_count=completed_count),
        recommendation_callout=_daily_recommendation_callout(due_count=due_count),
    )


def submit_daily_answer_response(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
    confidence: int,
) -> DailyEvaluationAnswerResponse:
    attempt, is_correct = submit_answer(
        session,
        user=user,
        assessment_session_id=assessment_session_id,
        question_id=question_id,
        option_id=option_id,
        confidence=confidence,
    )
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.id == assessment_session_id,
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "daily_evaluation",
        )
        .options(selectinload(AssessmentSession.questions))
    )
    completed = False
    session_status = "active"
    if assessment is not None:
        completed_question_ids = _answered_question_ids(session, assessment_id=assessment.id)
        completed = bool(assessment.questions) and len(completed_question_ids) >= len(assessment.questions)
        if completed:
            assessment.status = "completed"
            assessment.completed_at = datetime.now(UTC)
            session.commit()
        session_status = assessment.status
    return DailyEvaluationAnswerResponse(
        attempt_id=attempt.id,
        is_correct=is_correct,
        next_review_label="Review tomorrow" if not is_correct else "Review in 3 days",
        mastery_delta=0.08 if is_correct else -0.04,
        session_status=session_status,
        completed=completed,
    )


def get_daily_evaluation_result(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
) -> DailyEvaluationResultResponse | None:
    assessment = session.scalar(
        select(AssessmentSession)
        .where(
            AssessmentSession.id == assessment_session_id,
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "daily_evaluation",
        )
        .options(selectinload(AssessmentSession.questions))
    )
    if assessment is None:
        return None

    attempts = list(
        session.scalars(
            select(AssessmentAttempt)
            .where(AssessmentAttempt.session_id == assessment.id)
            .order_by(AssessmentAttempt.submitted_at)
        )
    )
    reviewed_count = len(attempts)
    correct_count = len([attempt for attempt in attempts if attempt.score >= 1.0])
    review_again_count = max(0, reviewed_count - correct_count)
    score_percent = int(round((correct_count / reviewed_count) * 100)) if reviewed_count else 0
    interval_days = 3 if review_again_count else 7
    due_date = datetime.now(UTC).date() + timedelta(days=interval_days)

    if assessment.questions and len(_answered_question_ids(session, assessment_id=assessment.id)) >= len(
        assessment.questions
    ):
        assessment.status = "completed"
        assessment.completed_at = assessment.completed_at or datetime.now(UTC)
        session.commit()

    reviewed_concepts = _reviewed_concepts(session, user=user, assessment=assessment, attempts=attempts)
    return DailyEvaluationResultResponse(
        session_id=assessment.id,
        title=assessment.title,
        status=assessment.status,
        source=_daily_source(assessment),
        score_percent=score_percent,
        reviewed_count=reviewed_count,
        correct_count=correct_count,
        review_again_count=review_again_count,
        reviewed_concepts=reviewed_concepts,
        spaced_repetition_impact=SpacedRepetitionImpactRead(
            retention_lift_percent=_retention_lift_percent(correct_count, review_again_count),
            days_until_next_review=interval_days,
            summary="You've strengthened your memory." if reviewed_count else "No review evidence yet.",
        ),
        next_review=DailyEvaluationNextReviewRead(
            label=f"Review in {interval_days} days",
            due_date=due_date.isoformat(),
            interval_days=interval_days,
        ),
        recommended_next_actions=_daily_next_actions(
            reviewed_concepts=reviewed_concepts,
            review_again_count=review_again_count,
            due_date=due_date,
        ),
        back_to_home=ActionRead(
            label="Back to Home",
            action_type="navigate",
            target="/home",
        ),
    )


def ensure_curriculum_seeded(session: Session) -> None:
    if session.scalar(select(Subject.id).limit(1)) is None:
        seed_curriculum(session, commit=False)
        session.flush()


def question_to_schema(question: AssessmentQuestion) -> AssessmentQuestionRead:
    return AssessmentQuestionRead(
        id=str(question.id),
        step_label=question.step_label,
        topic=question.topic,
        prompt=question.prompt,
        helper=question.helper_text,
        options=[
            AssessmentOptionRead(id=str(option.id), label=option.label, text=option.text)
            for option in question.options
        ],
    )


def track_to_schema(track: LearningTrack) -> TrackRead:
    return TrackRead(
        id=track.id,
        learning_goal_id=track.learning_goal_id,
        title=track.title,
        subtitle=track.subtitle,
        status=track.status,
        progress_percent=track.progress_percent,
        modules=[
            TrackModuleRead(
                id=module.id,
                track_id=module.track_id,
                title=module.title,
                description=module.description,
                estimated_minutes=module.estimated_minutes,
                difficulty_label=module.difficulty_label,
                sort_order=module.sort_order,
                status=module.status,
            )
            for module in track.modules
        ],
    )


def media_artifact_to_schema(artifact: MediaArtifact) -> MediaArtifactRead:
    playback_url = artifact.playback_url or artifact.video_url
    return MediaArtifactRead(
        id=artifact.id,
        title=artifact.title,
        subtitle=artifact.subtitle,
        artifact_type=artifact.artifact_type,
        status=artifact.status,
        duration_seconds=artifact.duration_seconds,
        duration_label=_duration_label(artifact.duration_seconds),
        thumbnail_url=artifact.thumbnail_url,
        playback_url=playback_url,
        transcript=artifact.transcript,
        notes=artifact.notes_json,
        track_id=artifact.track_id,
        module_id=artifact.module_id,
        created_at=artifact.created_at.isoformat() if artifact.created_at else "",
    )


def _user_tracks(session: Session, *, user: UserAccount) -> list[LearningTrack]:
    return list(
        session.scalars(
            select(LearningTrack)
            .where(LearningTrack.user_id == user.id)
            .options(selectinload(LearningTrack.modules))
            .order_by(LearningTrack.created_at.desc())
        )
    )


def _build_queue_items(tracks: list[LearningTrack]) -> list[QueueItemRead]:
    items: list[QueueItemRead] = []
    for track in tracks:
        modules = sorted(track.modules, key=lambda item: item.sort_order)
        ready_module = next(
            (module for module in modules if module.status in {"ready", "active"}),
            modules[0] if modules else None,
        )
        if ready_module is None:
            continue
        items.append(
            QueueItemRead(
                id=f"module:{ready_module.id}",
                track_id=track.id,
                module_id=ready_module.id,
                title=ready_module.title,
                subtitle=track.title,
                meta=f"{ready_module.estimated_minutes} min | {ready_module.difficulty_label}",
                status=ready_module.status,
                estimated_minutes=ready_module.estimated_minutes,
                action_label="Continue",
            )
        )
    if items:
        return items
    return [
        QueueItemRead(
            id="seed:create-goal",
            title="Create your first learning goal",
            subtitle="WICARA will generate a pretest, track, and modules from backend data.",
            meta="2 min setup",
            status="ready",
            estimated_minutes=2,
            action_label="Create goal",
        )
    ]


def _today_daily_session(session: Session, *, user: UserAccount) -> AssessmentSession | None:
    today = datetime.now(UTC).date().isoformat()
    return session.scalar(
        select(AssessmentSession).where(
            AssessmentSession.user_id == user.id,
            AssessmentSession.session_type == "daily_evaluation",
            AssessmentSession.metadata_json["review_date"].as_string() == today,
        )
    )


def _ensure_sample_media_artifacts(session: Session, *, user: UserAccount) -> None:
    if session.scalar(select(MediaArtifact.id).where(MediaArtifact.user_id == user.id).limit(1)):
        return
    tracks = _user_tracks(session, user=user)
    track = tracks[0] if tracks else None
    first_module = track.modules[0] if track and track.modules else None
    second_module = track.modules[1] if track and len(track.modules) > 1 else None
    samples = [
        {
            "module": first_module,
            "title": "Limits from graphs",
            "subtitle": "Approaching a value without touching it",
            "duration_seconds": 258,
            "transcript": "A limit describes the value a graph approaches as x gets close to a point.",
            "notes": [
                "Generated as durable seeded media so the gallery is not frontend-only.",
                "Connect this with the prerequisite checkpoint before derivative rules.",
            ],
        },
        {
            "module": second_module,
            "title": "Derivatives intuition",
            "subtitle": "What does a derivative tell us?",
            "duration_seconds": 405,
            "transcript": "A derivative measures local rate of change and appears as tangent slope.",
            "notes": [
                "Use the tangent-line idea before memorizing rules.",
                "Canvas evidence can later attach a learner's own graph sketch.",
            ],
        },
    ]
    for sample in samples:
        module = sample["module"]
        session.add(
            MediaArtifact(
                user_id=user.id,
                track_id=track.id if track else None,
                module_id=module.id if module else None,
                concept_id=module.concept_id if module else None,
                artifact_type="video",
                title=str(sample["title"]),
                subtitle=str(sample["subtitle"]),
                status="ready",
                duration_seconds=int(sample["duration_seconds"]),
                thumbnail_url="",
                playback_url="",
                transcript=str(sample["transcript"]),
                notes_json=list(sample["notes"]),
                metadata_json={"seed_source": "media_gallery_mvp"},
            )
        )
    session.commit()


def _date_range_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    start_at = datetime(start.year, start.month, start.day, tzinfo=UTC)
    exclusive_end = end + timedelta(days=1)
    end_at = datetime(exclusive_end.year, exclusive_end.month, exclusive_end.day, tzinfo=UTC)
    return start_at, end_at


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _assessment_attempt_rows(
    session: Session,
    *,
    user: UserAccount,
    submitted_from: datetime | None = None,
    submitted_before: datetime | None = None,
) -> list[tuple[AssessmentAttempt, AssessmentQuestion]]:
    query = (
        select(AssessmentAttempt, AssessmentQuestion)
        .join(AssessmentSession, AssessmentAttempt.session_id == AssessmentSession.id)
        .join(AssessmentQuestion, AssessmentAttempt.question_id == AssessmentQuestion.id)
        .where(AssessmentSession.user_id == user.id)
        .order_by(AssessmentAttempt.submitted_at)
    )
    if submitted_from is not None:
        query = query.where(AssessmentAttempt.submitted_at >= submitted_from)
    if submitted_before is not None:
        query = query.where(AssessmentAttempt.submitted_at < submitted_before)
    return [(attempt, question) for attempt, question in session.execute(query)]


def _attempt_correct_percent(rows: list[tuple[AssessmentAttempt, AssessmentQuestion]]) -> int:
    if not rows:
        return 0
    correct = len([attempt for attempt, _question in rows if attempt.score >= 1.0])
    return int(round((correct / len(rows)) * 100))


def _weighted_analysis_percent(rows: list[tuple[AssessmentAttempt, AssessmentQuestion]]) -> int:
    if not rows:
        return 0
    weighted_score = 0.0
    total_weight = 0.0
    for attempt, _question in rows:
        confidence_weight = max(1, min(10, attempt.confidence or 1)) / 10
        total_weight += confidence_weight
        weighted_score += (attempt.score or 0.0) * confidence_weight
    return int(round((weighted_score / max(total_weight, 0.01)) * 100))


def _application_rows(
    rows: list[tuple[AssessmentAttempt, AssessmentQuestion]],
) -> list[tuple[AssessmentAttempt, AssessmentQuestion]]:
    selected: list[tuple[AssessmentAttempt, AssessmentQuestion]] = []
    for row in rows:
        _attempt, question = row
        marker = f"{question.topic} {question.helper_text} {question.difficulty_label}".lower()
        if any(token in marker for token in ("application", "apply", "problem", "equation")):
            selected.append(row)
    return selected or rows


def _report_period_value(
    rows: list[tuple[AssessmentAttempt, AssessmentQuestion]],
    *,
    fallback: int,
    analysis: bool = False,
) -> int:
    if not rows:
        return fallback
    return _weighted_analysis_percent(rows) if analysis else _attempt_correct_percent(rows)


def _report_trends(
    *,
    range_attempts: list[tuple[AssessmentAttempt, AssessmentQuestion]],
    baseline_attempts: list[tuple[AssessmentAttempt, AssessmentQuestion]],
) -> list[ReportTrendRead]:
    if not range_attempts and not baseline_attempts:
        return [
            ReportTrendRead(label="Overall", before=0.56, after=0.72),
            ReportTrendRead(label="Application", before=0.48, after=0.66),
            ReportTrendRead(label="Analysis", before=0.44, after=0.62),
        ]

    overall_after = _report_period_value(range_attempts, fallback=_attempt_correct_percent(baseline_attempts))
    overall_before = _report_period_value(baseline_attempts, fallback=max(18, overall_after - 16))

    range_application = _application_rows(range_attempts)
    baseline_application = _application_rows(baseline_attempts)
    application_after = _report_period_value(range_application, fallback=max(18, overall_after - 4))
    application_before = _report_period_value(
        baseline_application,
        fallback=max(18, application_after - 18),
    )

    analysis_after = _report_period_value(range_attempts, fallback=max(18, overall_after - 8), analysis=True)
    analysis_before = _report_period_value(
        baseline_attempts,
        fallback=max(18, analysis_after - 20),
        analysis=True,
    )

    return [
        ReportTrendRead(label="Overall", before=overall_before / 100, after=overall_after / 100),
        ReportTrendRead(
            label="Application",
            before=application_before / 100,
            after=application_after / 100,
        ),
        ReportTrendRead(label="Analysis", before=analysis_before / 100, after=analysis_after / 100),
    ]


def _recent_concept_names(session: Session, *, user: UserAccount) -> list[str]:
    rows = session.execute(
        select(KnowledgeConcept.title)
        .join(LearnerConceptState, LearnerConceptState.concept_id == KnowledgeConcept.id)
        .where(LearnerConceptState.user_id == user.id)
        .order_by(LearnerConceptState.last_evaluated_at.desc().nullslast())
        .limit(3)
    )
    return [str(row[0]) for row in rows]


def _weekly_recommendations(
    *,
    session: Session,
    user: UserAccount,
    states: list[LearnerConceptState],
    remaining_gaps: int,
    week_end: date,
) -> list[UpcomingRecommendationRead]:
    state_rows = session.execute(
        select(LearnerConceptState, KnowledgeConcept)
        .join(KnowledgeConcept, LearnerConceptState.concept_id == KnowledgeConcept.id)
        .where(LearnerConceptState.user_id == user.id)
        .order_by(
            LearnerConceptState.next_review_at.asc().nullslast(),
            LearnerConceptState.mastery_score.asc(),
        )
        .limit(3)
    )
    recommendations: list[UpcomingRecommendationRead] = []
    today = datetime.now(UTC).date()
    for priority, (state, concept) in enumerate(state_rows, start=1):
        due_date = state.next_review_at.date() if state.next_review_at else today + timedelta(days=priority + 1)
        if state.status == "review_due" or due_date <= today + timedelta(days=2):
            action_type = "review"
            title = f"Review: {concept.title}"
            reason = "Next review is due soon based on spaced repetition state."
        elif state.mastery_score < 0.55:
            action_type = "practice"
            title = f"Practice: {concept.title}"
            reason = "Mastery is still low, so retrieval practice is the highest-leverage action."
        elif state.mastery_score < 0.75:
            action_type = "deepen"
            title = f"Deepen: {concept.title}"
            reason = "Strengthen transfer before the next post-test."
        else:
            action_type = "continue_learning"
            title = "Continue: next module"
            reason = f"{concept.title} is stable enough to continue the path."
        recommendations.append(
            UpcomingRecommendationRead(
                title=title,
                action_type=action_type,
                reason=reason,
                due_date=due_date.isoformat(),
                due_label=_due_label(due_date, today=today),
            )
        )
    if recommendations:
        return recommendations

    concept_names = _recent_concept_names(session, user=user)
    weak_concept = concept_names[0] if concept_names else "Market Equilibrium"
    deepen_concept = concept_names[1] if len(concept_names) > 1 else "Elasticity"
    practice_due = week_end + timedelta(days=1)
    reason = (
        f"{remaining_gaps} gaps still need spaced review."
        if states
        else "Seeded recommendation until the learner has enough mastery history."
    )
    return [
        UpcomingRecommendationRead(
            title=f"Review: {weak_concept}",
            action_type="review",
            reason=reason,
            due_date=(today + timedelta(days=2)).isoformat(),
            due_label="Due in 2 days",
        ),
        UpcomingRecommendationRead(
            title=f"Deepen: {deepen_concept}",
            action_type="deepen",
            reason="Strengthen concept transfer before the next post-test.",
            due_date=(today + timedelta(days=4)).isoformat(),
            due_label="Due in 4 days",
        ),
        UpcomingRecommendationRead(
            title="Practice: Application Set 2",
            action_type="practice",
            reason="Application trend is the highest-leverage next check.",
            due_date=practice_due.isoformat(),
            due_label="Due this week",
        ),
    ]


def _due_label(due_date: date, *, today: date) -> str:
    day_delta = (due_date - today).days
    if day_delta < 0:
        return "Overdue"
    if day_delta == 0:
        return "Due today"
    if day_delta == 1:
        return "Due tomorrow"
    return f"Due in {day_delta} days"


def _answered_question_ids(session: Session, *, assessment_id: UUID) -> set[UUID]:
    return set(
        session.scalars(
            select(AssessmentAttempt.question_id).where(
                AssessmentAttempt.session_id == assessment_id
            )
        )
    )


def _language_for_user(user: UserAccount) -> str:
    if user.learner_profile and user.learner_profile.preferred_language:
        return user.learner_profile.preferred_language
    return "en"


def _daily_source(assessment: AssessmentSession) -> str:
    policy = assessment.metadata_json.get("policy")
    if policy == "spaced_repetition_mvp":
        return "seeded_spaced_repetition_mvp"
    return str(assessment.metadata_json.get("generation") or "deterministic_mvp")


def _retention_forecast(*, completed_count: int) -> RetentionForecastRead:
    lift = min(12, completed_count * 2)
    raw_points = [
        ("Today", 100, False),
        ("Day 1", 70 + lift, False),
        ("Day 2", 52 + lift, False),
        ("Day 7", 38 + lift, False),
        ("Day 14", 25 + lift, True),
        ("Day 30", 17 + lift, True),
    ]
    return RetentionForecastRead(
        title="Your retention forecast",
        basis="Based on the Ebbinghaus forgetting curve MVP.",
        points=[
            RetentionForecastPointRead(
                label=label,
                retention_percent=min(100, percent),
                projected=projected,
            )
            for label, percent, projected in raw_points
        ],
    )


def _daily_recommendation_callout(*, due_count: int) -> RecommendationCalloutRead:
    return RecommendationCalloutRead(
        title="Review now",
        message=(
            "Keep reviewing to move the curve up and improve long-term retention."
            if due_count
            else "You are caught up for today's review queue."
        ),
        impact_label="High impact" if due_count else "Maintained",
        action_label="Review now" if due_count else "Back to home",
    )


def _reviewed_concepts(
    session: Session,
    *,
    user: UserAccount,
    assessment: AssessmentSession,
    attempts: list[AssessmentAttempt],
) -> list[ReviewedConceptRead]:
    latest_attempt_by_question: dict[UUID, AssessmentAttempt] = {}
    for attempt in attempts:
        latest_attempt_by_question[attempt.question_id] = attempt

    concept_ids = {
        question.concept_id
        for question in assessment.questions
        if question.concept_id is not None
    }
    concept_titles: dict[UUID, str] = {}
    state_by_concept: dict[UUID, LearnerConceptState] = {}
    if concept_ids:
        concept_titles = {
            concept.id: concept.title
            for concept in session.scalars(
                select(KnowledgeConcept).where(KnowledgeConcept.id.in_(concept_ids))
            )
        }
        state_by_concept = {
            state.concept_id: state
            for state in session.scalars(
                select(LearnerConceptState).where(
                    LearnerConceptState.user_id == user.id,
                    LearnerConceptState.concept_id.in_(concept_ids),
                )
            )
        }

    rows: list[ReviewedConceptRead] = []
    for question in sorted(assessment.questions, key=lambda item: item.sort_order):
        attempt = latest_attempt_by_question.get(question.id)
        if attempt is None:
            continue
        state = state_by_concept.get(question.concept_id) if question.concept_id else None
        mastery_score = state.mastery_score if state else (0.68 if attempt.score >= 1.0 else 0.32)
        rows.append(
            ReviewedConceptRead(
                concept_id=str(question.concept_id) if question.concept_id else None,
                title=(
                    concept_titles.get(question.concept_id)
                    if question.concept_id
                    else question.topic
                )
                or question.topic,
                status_label=_concept_status_label(
                    is_correct=attempt.score >= 1.0,
                    mastery_score=mastery_score,
                ),
                mastery_score=round(float(mastery_score), 2),
            )
        )
    return rows


def _concept_status_label(*, is_correct: bool, mastery_score: float) -> str:
    if not is_correct:
        return "Review"
    if mastery_score >= 0.78:
        return "Strong"
    return "Good"


def _retention_lift_percent(correct_count: int, review_again_count: int) -> int:
    return max(0, min(40, 12 + (correct_count * 5) - (review_again_count * 2)))


def _daily_next_actions(
    *,
    reviewed_concepts: list[ReviewedConceptRead],
    review_again_count: int,
    due_date: date,
) -> list[RecommendedNextActionRead]:
    review_concept = next(
        (concept for concept in reviewed_concepts if concept.status_label == "Review"),
        reviewed_concepts[0] if reviewed_concepts else None,
    )
    practice_concept = next(
        (
            concept
            for concept in reviewed_concepts
            if concept.status_label != "Review" and concept.mastery_score < 0.75
        ),
        review_concept,
    )
    return [
        RecommendedNextActionRead(
            title=(
                f"Review: {review_concept.title}"
                if review_concept and review_again_count
                else (
                    f"Review: {review_concept.title}"
                    if review_concept
                    else "Review 2-week concepts"
                )
            ),
            action_type="review",
            reason=(
                "You missed this concept in today's evaluation."
                if review_again_count
                else "Focus on high-impact memory reinforcement."
            ),
            due_date=due_date.isoformat(),
            priority=1,
        ),
        RecommendedNextActionRead(
            title=(
                f"Practice: {practice_concept.title}"
                if practice_concept and practice_concept.mastery_score < 0.75
                else "Practice 5 more questions"
            ),
            action_type="practice",
            reason="Retighten your understanding with short retrieval practice.",
            due_date=(datetime.now(UTC).date() + timedelta(days=1)).isoformat(),
            priority=2,
        ),
        RecommendedNextActionRead(
            title="Continue learning",
            action_type="continue_learning",
            reason="Go to your learning path when review is complete.",
            due_date=None,
            priority=3,
        ),
    ]


def _display_name_for_user(user: UserAccount) -> str:
    if user.learner_profile and user.learner_profile.full_name.strip():
        return user.learner_profile.full_name.strip()
    return user.display_name or "Learner"


def _first_name(display_name: str) -> str:
    parts = display_name.strip().split()
    return parts[0] if parts else "Learner"


def _streak_days(session: Session, *, user: UserAccount) -> int:
    active_days = session.scalar(
        select(func.count(func.distinct(func.date(AssessmentAttempt.submitted_at))))
        .join(AssessmentSession, AssessmentAttempt.session_id == AssessmentSession.id)
        .where(AssessmentSession.user_id == user.id)
    )
    return int(active_days or 0)


def _duration_label(seconds: int) -> str:
    minutes, remainder = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


def _current_week_label() -> str:
    start, end = _current_week_range()
    return _format_week_label(start, end)


def _current_week_range() -> tuple[date, date]:
    today = datetime.now(UTC).date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def _format_week_label(start: date, end: date) -> str:
    return f"{start.strftime('%b')} {start.day} - {end.strftime('%b')} {end.day}, {end.year}"


def _create_assessment_session(
    session: Session,
    *,
    user: UserAccount,
    learning_goal: LearningGoal | None,
    track: LearningTrack | None,
    session_type: str,
    title: str,
    templates: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> AssessmentSession:
    assessment = AssessmentSession(
        user_id=user.id,
        learning_goal_id=learning_goal.id if learning_goal else None,
        track_id=track.id if track else None,
        session_type=session_type,
        title=title,
        status="active",
        metadata_json=metadata or {"generation": "deterministic_seed"},
    )
    session.add(assessment)
    session.flush()

    for index, template in enumerate(templates, start=1):
        concept = _find_concept_by_hints(session, template["concept_hints"])
        question = AssessmentQuestion(
            session_id=assessment.id,
            concept_id=concept.id if concept else None,
            step_label=f"{index} / {len(templates)}"
            if session_type == "pretest"
            else "Daily Evals",
            topic=str(template["topic"]),
            prompt=str(template["prompt"]),
            helper_text=str(template["helper"]),
            difficulty_label="Medium",
            sort_order=index,
            metadata_json={
                "seed_source": f"{session_type}_template",
                "correct_option_key": template["correct"],
            },
        )
        session.add(question)
        session.flush()

        for option_index, (key, text) in enumerate(template["options"], start=1):
            session.add(
                AssessmentOption(
                    question_id=question.id,
                    option_key=key,
                    label=key,
                    text=text,
                    is_correct=key == template["correct"],
                    sort_order=option_index,
                )
            )
    session.flush()
    return assessment


def _create_track(
    session: Session,
    *,
    user: UserAccount,
    goal: LearningGoal,
    subject: Subject,
    concept: KnowledgeConcept | None,
) -> LearningTrack:
    title = f"{goal.normalized_topic} path"
    track = LearningTrack(
        user_id=user.id,
        learning_goal_id=goal.id,
        title=title,
        subtitle=f"{subject.name} | prerequisite-first adaptive path",
        status="pretest",
        progress_percent=0,
        metadata_json={"generation": "deterministic_seed"},
    )
    session.add(track)
    session.flush()

    modules = _module_templates(goal.normalized_topic, concept)
    for index, module in enumerate(modules, start=1):
        session.add(
            TrackModule(
                track_id=track.id,
                concept_id=concept.id if concept and index == 2 else None,
                title=module["title"],
                description=module["description"],
                estimated_minutes=module["minutes"],
                difficulty_label=module["difficulty"],
                sort_order=index,
                status="ready" if index == 1 else "locked",
                metadata_json={"seed_source": "learning_goal_track"},
            )
        )
    session.flush()
    return track


def _module_templates(
    normalized_topic: str,
    concept: KnowledgeConcept | None,
) -> list[dict[str, Any]]:
    target = concept.title if concept else normalized_topic
    return [
        {
            "title": "Prerequisite checkpoint",
            "description": "Repair the foundation detected by the pretest before starting the main topic.",
            "minutes": 8,
            "difficulty": "Easy",
        },
        {
            "title": target,
            "description": f"Learn {normalized_topic} with chat, canvas evidence, and short checks.",
            "minutes": 14,
            "difficulty": "Medium",
        },
        {
            "title": "Application and review",
            "description": "Apply the concept, then schedule it for spaced repetition.",
            "minutes": 10,
            "difficulty": "Medium",
        },
    ]


def _resolve_subject(
    session: Session,
    *,
    subject_code: str | None,
    user: UserAccount,
) -> Subject:
    candidates = []
    if subject_code:
        candidates.append(subject_code)
    profile = user.learner_profile
    if profile:
        candidates.extend(profile.selected_subjects)
    candidates.extend(["matematika", "math"])

    for candidate in candidates:
        normalized = canonical_subject_code(candidate)
        subject = session.scalar(
            select(Subject).where(Subject.code == normalized, Subject.is_active.is_(True))
        )
        if subject is not None:
            return subject

    subject = session.scalar(select(Subject).where(Subject.is_active.is_(True)))
    if subject is None:
        raise ValueError("Curriculum seed is empty.")
    return subject


def _pick_concept(
    session: Session,
    *,
    subject: Subject,
    raw_topic: str,
) -> KnowledgeConcept | None:
    topic = raw_topic.lower()
    concepts = list(
        session.scalars(
            select(KnowledgeConcept)
            .where(KnowledgeConcept.subject_id == subject.id)
            .order_by(KnowledgeConcept.display_order, KnowledgeConcept.title)
        )
    )
    if not concepts:
        return None
    for concept in concepts:
        haystack = f"{concept.code} {concept.title}".lower()
        if any(token in haystack for token in topic.replace("-", " ").split()):
            return concept
    for hint in ("intuitive_limits", "derivative_definition", "km_d_matematika_bilangan_rasional"):
        for concept in concepts:
            if concept.code == hint:
                return concept
    return concepts[0]


def _find_concept_by_hints(
    session: Session,
    hints: list[str],
) -> KnowledgeConcept | None:
    for hint in hints:
        concept = session.scalar(select(KnowledgeConcept).where(KnowledgeConcept.code == hint))
        if concept is not None:
            return concept
    return session.scalar(select(KnowledgeConcept).order_by(KnowledgeConcept.display_order))


def _publish_media_job_to_queue(*, job_id: UUID) -> bool:
    try:
        adapter = build_media_job_queue_adapter()
        adapter.enqueue(job_id=job_id)
        return True
    except Exception:
        logger.exception("Failed to enqueue media job %s to queue backend.", job_id)
        return False


def _load_job_with_artifact(
    session: Session,
    *,
    job_id: UUID,
) -> tuple[MediaJob, MediaArtifact] | None:
    return session.execute(
        select(MediaJob, MediaArtifact)
        .join(MediaArtifact, MediaArtifact.id == MediaJob.artifact_id)
        .where(MediaJob.id == job_id)
    ).first()


def _initial_render_meta(
    *,
    validation_result: Any | None,
    validation_error: dict[str, Any] | None,
) -> dict[str, Any]:
    render_meta: dict[str, Any] = {}
    if validation_result is not None:
        render_meta.update(
            {
                "template_path": validation_result.template_path,
                "scene_class": validation_result.scene_class,
                "schema_id": validation_result.schema_id,
                "resolved_from": validation_result.resolved_from,
                "used_alias": validation_result.used_alias,
            }
        )
    if validation_error is not None:
        render_meta["error_details"] = validation_error
        render_meta["error_code"] = validation_error.get("code")
    return render_meta


def _mark_job_processing(
    session: Session,
    *,
    job: MediaJob,
    artifact: MediaArtifact,
) -> None:
    if job.status == "processing":
        return
    if job.status != "queued":
        raise ValueError(f"Job {job.id} is not claimable from status '{job.status}'.")
    job.status = "processing"
    job.progress = max(5, int(job.progress or 0))
    job.message = "Worker claimed job and started processing."
    job.error = None
    job.attempt = int(job.attempt or 0) + 1
    if job.started_at is None:
        job.started_at = datetime.now(UTC)
    artifact.status = "processing"
    _sync_artifact_job_state(
        artifact=artifact,
        job=job,
        error_message=None,
        error_details=None,
        error_code=None,
    )
    session.commit()


def _update_job_progress(
    session: Session,
    *,
    job: MediaJob,
    artifact: MediaArtifact,
    progress: int,
    message: str,
) -> None:
    job.status = "processing"
    job.progress = max(0, min(100, int(progress)))
    job.message = message
    artifact.status = "processing"
    _sync_artifact_job_state(
        artifact=artifact,
        job=job,
        error_message=None,
        error_details=None,
        error_code=None,
    )
    session.commit()


def _mark_job_ready(
    session: Session,
    *,
    job: MediaJob,
    artifact: MediaArtifact,
    final_message: str | None = None,
) -> None:
    job.status = "ready"
    job.progress = 100
    job.message = final_message or "Render lifecycle finished. Artifact is ready."
    job.error = None
    job.finished_at = datetime.now(UTC)
    artifact.status = "ready"
    _sync_artifact_job_state(
        artifact=artifact,
        job=job,
        error_message=None,
        error_details=None,
        error_code=None,
    )
    session.commit()


def _mark_job_failed(
    session: Session,
    *,
    job: MediaJob,
    artifact: MediaArtifact,
    error_message: str,
    error_code: str | None = None,
    error_details: dict[str, Any] | None = None,
) -> None:
    cleaned_error = (error_message or "Unknown media worker error.").strip()[:2000]
    job.status = "failed"
    job.message = "Render lifecycle failed."
    job.error = cleaned_error
    job.finished_at = datetime.now(UTC)
    artifact.status = "failed"
    _sync_artifact_job_state(
        artifact=artifact,
        job=job,
        error_message=cleaned_error,
        error_details=error_details,
        error_code=error_code,
    )
    session.commit()


def _validate_job_payload(
    *,
    session: Session,
    job: MediaJob,
    artifact: MediaArtifact,
) -> None:
    if not artifact.template_id.strip():
        raise ValueError(f"Job {job.id} has empty template_id.")
    if not isinstance(artifact.spec_json, dict):
        raise ValueError(f"Job {job.id} has invalid spec_json payload.")
    validation_result = validate_template_spec(
        template_id=artifact.template_id,
        spec_json=artifact.spec_json,
    )
    artifact.template_id = validation_result.template_id
    artifact.spec_json = validation_result.normalized_spec
    render_meta = dict(artifact.render_meta_json or {})
    render_meta.update(
        {
            "template_path": validation_result.template_path,
            "scene_class": validation_result.scene_class,
            "schema_id": validation_result.schema_id,
            "resolved_from": validation_result.resolved_from,
            "used_alias": validation_result.used_alias,
        }
    )
    artifact.render_meta_json = render_meta
    session.flush()


def _render_artifact_with_retry(
    session: Session,
    *,
    job: MediaJob,
    artifact: MediaArtifact,
    max_attempts: int,
    timeout_seconds: int,
) -> tuple[RenderOutput, int]:
    attempts_limit = max(1, int(max_attempts))
    render_meta = dict(artifact.render_meta_json or {})
    template_path = str(render_meta.get("template_path", "")).strip()
    scene_class = str(render_meta.get("scene_class", "GeneratedTemplate")).strip()
    if not template_path:
        raise RenderEngineError(
            code="render_error",
            message="Render metadata does not contain template_path.",
            details={"job_id": str(job.id), "template_id": artifact.template_id},
        )

    last_error: RenderEngineError | None = None
    for attempt in range(1, attempts_limit + 1):
        _update_job_progress(
            session,
            job=job,
            artifact=artifact,
            progress=60,
            message=f"Running Manim render attempt {attempt}/{attempts_limit}.",
        )
        try:
            output = render_template_scene(
                job_id=job.id,
                template_path=template_path,
                scene_class=scene_class,
                spec_json=artifact.spec_json,
                quality_profile=artifact.quality_profile,
                timeout_seconds=timeout_seconds,
            )
            return output, attempt
        except RenderEngineError as exc:
            last_error = exc
            if attempt < attempts_limit:
                _update_job_progress(
                    session,
                    job=job,
                    artifact=artifact,
                    progress=68,
                    message=f"Render attempt {attempt} failed. Retrying attempt {attempt + 1}/{attempts_limit}.",
                )
                continue
            break

    assert last_error is not None
    raise last_error


def _attach_render_output_to_artifact(
    session: Session,
    *,
    artifact: MediaArtifact,
    render_output: RenderOutput,
    attempts_used: int,
) -> None:
    artifact.video_url = render_output.video_path
    artifact.playback_url = render_output.video_path
    render_meta = dict(artifact.render_meta_json or {})
    render_meta.update(
        {
            "local_video_path": render_output.video_path,
            "relative_video_path": render_output.relative_video_path,
            "render_attempts_used": attempts_used,
            "render_completed_at": datetime.now(UTC).isoformat(),
            "manim_stdout_tail": render_output.stdout,
            "manim_stderr_tail": render_output.stderr,
        }
    )
    artifact.render_meta_json = render_meta
    session.flush()


def _sync_artifact_job_state(
    *,
    artifact: MediaArtifact,
    job: MediaJob,
    error_message: str | None,
    error_details: dict[str, Any] | None,
    error_code: str | None,
) -> None:
    metadata = dict(artifact.metadata_json or {})
    metadata.update(
        {
            "progress": max(0, min(100, int(job.progress or 0))),
            "job_state": job.status,
            "job_id": str(job.id),
        }
    )
    if error_message:
        metadata["error"] = error_message
        if error_code:
            metadata["error_code"] = error_code
    else:
        metadata.pop("error", None)
        metadata.pop("error_code", None)
    artifact.metadata_json = metadata

    render_meta = dict(artifact.render_meta_json or {})
    render_meta.update(
        {
            "last_job_message": job.message,
            "attempt": int(job.attempt or 0),
            "worker_status": job.status,
        }
    )
    if error_message:
        render_meta["error"] = error_message
        if error_code:
            render_meta["error_code"] = error_code
    else:
        render_meta.pop("error", None)
        render_meta.pop("error_code", None)
    if error_details:
        render_meta["error_details"] = error_details
    else:
        render_meta.pop("error_details", None)
    artifact.render_meta_json = render_meta


def _resolve_owned_workspace(
    session: Session,
    *,
    user: UserAccount,
    workspace_id: UUID | None,
) -> WorkspaceSession | None:
    if workspace_id is None:
        return None
    workspace = session.scalar(
        select(WorkspaceSession).where(
            WorkspaceSession.id == workspace_id,
            WorkspaceSession.user_id == user.id,
        )
    )
    if workspace is None:
        raise LookupError("Workspace session was not found.")
    return workspace


def _resolve_concept_id(
    session: Session,
    *,
    concept_id: UUID | None,
    workspace: WorkspaceSession | None,
) -> UUID | None:
    if concept_id is not None:
        concept = session.get(KnowledgeConcept, concept_id)
        if concept is None:
            raise LookupError("Concept was not found.")
        return concept.id
    if workspace is None:
        return None
    module = session.get(TrackModule, workspace.module_id)
    if module is None:
        return None
    return module.concept_id


def _queued_artifact_title(spec_json: dict[str, Any], template_id: str) -> str:
    raw_title = spec_json.get("title")
    if isinstance(raw_title, str) and raw_title.strip():
        return raw_title.strip()[:255]
    return f"Generated video ({template_id})"


def _queued_artifact_subtitle(spec_json: dict[str, Any]) -> str:
    raw_subtitle = spec_json.get("subtitle")
    if isinstance(raw_subtitle, str) and raw_subtitle.strip():
        return raw_subtitle.strip()[:255]
    return "Queued for Manim rendering"


def _normalize_short_label(value: str, *, fallback: str, max_length: int) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return fallback
    return normalized[:max_length]


def _resolve_submission_targets(
    session: Session,
    *,
    user: UserAccount,
    assessment_session_id: UUID,
    question_id: str,
    option_id: str,
) -> tuple[AssessmentSession, AssessmentQuestion, AssessmentOption]:
    assessment = session.scalar(
        select(AssessmentSession)
        .where(AssessmentSession.id == assessment_session_id, AssessmentSession.user_id == user.id)
        .options(
            selectinload(AssessmentSession.questions).selectinload(AssessmentQuestion.options)
        )
    )
    if assessment is None:
        raise LookupError("Assessment session was not found.")

    question = _find_question(assessment.questions, question_id)
    if question is None:
        raise LookupError("Assessment question was not found.")
    option = _find_option(question.options, option_id)
    if option is None:
        raise LookupError("Assessment option was not found.")
    return assessment, question, option


def _find_question(
    questions: list[AssessmentQuestion],
    question_id: str,
) -> AssessmentQuestion | None:
    for question in questions:
        if str(question.id) == question_id:
            return question
    if len(questions) == 1:
        return questions[0]
    return None


def _find_option(
    options: list[AssessmentOption],
    option_id: str,
) -> AssessmentOption | None:
    normalized = option_id.strip()
    for option in options:
        if str(option.id) == normalized or option.option_key == normalized or option.label == normalized:
            return option
    return None


def _update_mastery(
    session: Session,
    *,
    user: UserAccount,
    question: AssessmentQuestion,
    is_correct: bool,
) -> None:
    if question.concept_id is None:
        return
    state = session.scalar(
        select(LearnerConceptState).where(
            LearnerConceptState.user_id == user.id,
            LearnerConceptState.concept_id == question.concept_id,
        )
    )
    if state is None:
        state = LearnerConceptState(
            user_id=user.id,
            concept_id=question.concept_id,
            status="ready",
            mastery_score=0.0,
            confidence_score=0.0,
            evidence_count=0,
        )
        session.add(state)
    delta = 0.18 if is_correct else -0.12
    mastery_score = state.mastery_score or 0.0
    confidence_score = state.confidence_score or 0.0
    state.mastery_score = max(0.0, min(1.0, mastery_score + delta))
    state.confidence_score = max(
        0.0,
        min(1.0, confidence_score + (0.12 if is_correct else -0.08)),
    )
    state.status = "review_due" if not is_correct else ("mastered" if state.mastery_score >= 0.7 else "ready")
    state.evidence_count = (state.evidence_count or 0) + 1
    state.last_evaluated_at = datetime.now(UTC)
    state.next_review_at = datetime.now(UTC) + (timedelta(days=3) if is_correct else timedelta(days=1))


def _normalize_topic(raw_topic: str) -> str:
    cleaned = " ".join(raw_topic.strip().split())
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "Learning goal"
