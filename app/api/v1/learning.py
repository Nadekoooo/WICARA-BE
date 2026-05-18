from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.learning import schemas, service

router = APIRouter()


@router.post("/learning-goals", response_model=schemas.LearningGoalCreateResponse)
def create_learning_goal(
    payload: schemas.LearningGoalCreateRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.LearningGoalCreateResponse:
    try:
        return service.create_learning_goal(
            session,
            user=account,
            raw_topic=payload.raw_topic,
            subject_code=payload.subject_code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/learning-goals/{learning_goal_id}", response_model=schemas.LearningGoalRead)
def read_learning_goal(
    learning_goal_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.LearningGoalRead:
    goal = service.read_learning_goal(session, user=account, learning_goal_id=learning_goal_id)
    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal was not found.")
    return goal


@router.get(
    "/learning-goals/{learning_goal_id}/assessment-dashboard",
    response_model=schemas.AssessmentDashboardResponse,
)
def assessment_dashboard(
    learning_goal_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.AssessmentDashboardResponse:
    dashboard = service.get_assessment_dashboard(
        session,
        user=account,
        learning_goal_id=learning_goal_id,
    )
    if dashboard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal was not found.")
    return dashboard


@router.get("/tracks", response_model=schemas.TrackListResponse)
def list_tracks(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.TrackListResponse:
    return service.list_tracks(session, user=account)


@router.get("/home", response_model=schemas.HomeSummaryResponse)
def home_summary(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.HomeSummaryResponse:
    return service.get_home_summary(session, user=account)


@router.get("/learning-queue", response_model=schemas.LearningQueueResponse)
def learning_queue(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.LearningQueueResponse:
    return service.get_learning_queue(session, user=account)


@router.post(
    "/animation/queue",
    response_model=schemas.AnimationQueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def queue_animation(
    payload: schemas.AnimationQueueRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.AnimationQueueResponse:
    try:
        return service.queue_animation_job(
            session,
            user=account,
            workspace_id=payload.workspace_id,
            concept_id=payload.concept_id,
            template_id=payload.template_id,
            spec_json=payload.spec_json,
            language=payload.language,
            quality_profile=payload.quality_profile,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get(
    "/animation/status/{job_id}",
    response_model=schemas.AnimationJobStatusResponse,
)
def animation_job_status(
    job_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.AnimationJobStatusResponse:
    job = service.get_animation_job_status(session, user=account, job_id=job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animation job was not found.",
        )
    return job


@router.get("/tracks/{track_id}/modules", response_model=schemas.TrackRead)
def track_modules(
    track_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.TrackRead:
    track = service.get_track_modules(session, user=account, track_id=track_id)
    if track is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track was not found.")
    return track


@router.patch(
    "/tracks/{track_id}/modules/{module_id}/state",
    response_model=schemas.TrackModuleStateUpdateResponse,
)
def update_track_module_state(
    track_id: UUID,
    module_id: UUID,
    payload: schemas.TrackModuleStateUpdateRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.TrackModuleStateUpdateResponse:
    try:
        result = service.update_track_module_state(
            session,
            user=account,
            track_id=track_id,
            module_id=module_id,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track module was not found.",
        )
    return result


@router.get("/media-artifacts", response_model=schemas.MediaArtifactListResponse)
def media_artifacts(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.MediaArtifactListResponse:
    return service.list_media_artifacts(session, user=account)


@router.get("/media-artifacts/{artifact_id}", response_model=schemas.MediaArtifactRead)
def media_artifact_detail(
    artifact_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.MediaArtifactRead:
    artifact = service.get_media_artifact(session, user=account, artifact_id=artifact_id)
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media artifact was not found.",
        )
    return artifact


@router.get(
    "/media-artifacts/{artifact_id}/status",
    response_model=schemas.MediaArtifactStatusResponse,
)
def media_artifact_status(
    artifact_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.MediaArtifactStatusResponse:
    artifact = service.get_media_artifact_status(session, user=account, artifact_id=artifact_id)
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media artifact was not found.",
        )
    return artifact


@router.get("/reports/weekly/latest", response_model=schemas.WeeklyReportResponse)
def latest_weekly_report(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.WeeklyReportResponse:
    return service.get_latest_weekly_report(session, user=account)


@router.get("/reports/weekly", response_model=schemas.WeeklyReportResponse)
def weekly_report(
    start: date = Query(...),
    end: date = Query(...),
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.WeeklyReportResponse:
    if start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Report start date must be before or equal to end date.",
        )
    if (end - start).days > 31:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Weekly report range cannot exceed 31 days.",
        )
    return service.get_weekly_report(session, user=account, start=start, end=end)


@router.get("/pretests/{learning_goal_id}", response_model=schemas.PretestReadResponse)
def read_pretest(
    learning_goal_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.PretestReadResponse:
    pretest = service.get_pretest_for_goal(session, user=account, learning_goal_id=learning_goal_id)
    if pretest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pretest was not found.")
    return pretest


@router.post(
    "/pretests/{assessment_session_id}/answers",
    response_model=schemas.SubmitAnswerResponse,
)
def submit_pretest_answer(
    assessment_session_id: UUID,
    payload: schemas.SubmitAnswerRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.SubmitAnswerResponse:
    try:
        return service.submit_answer_response(
            session,
            user=account,
            assessment_session_id=assessment_session_id,
            question_id=payload.question_id,
            option_id=payload.option_id,
            confidence=payload.confidence,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/pretests/{assessment_session_id}/reasoning",
    response_model=schemas.KnowledgeStateResponse,
)
def submit_pretest_reasoning(
    assessment_session_id: UUID,
    payload: schemas.SubmitReasoningRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.KnowledgeStateResponse:
    try:
        return service.submit_reasoning_response(
            session,
            user=account,
            assessment_session_id=assessment_session_id,
            question_id=payload.question_id,
            option_id=payload.option_id,
            confidence=payload.confidence,
            explanation=payload.explanation,
            used_canvas=payload.used_canvas,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/daily-evaluations/today", response_model=schemas.DailyEvaluationResponse)
def get_daily_evaluation(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.DailyEvaluationResponse:
    try:
        return service.get_or_create_daily_evaluation(session, user=account)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post(
    "/daily-evaluations/{assessment_session_id}/answers",
    response_model=schemas.DailyEvaluationAnswerResponse,
)
def submit_daily_evaluation_answer(
    assessment_session_id: UUID,
    payload: schemas.DailyEvaluationAnswerRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.DailyEvaluationAnswerResponse:
    try:
        return service.submit_daily_answer_response(
            session,
            user=account,
            assessment_session_id=assessment_session_id,
            question_id=payload.question_id,
            option_id=payload.option_id,
            confidence=payload.confidence,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/daily-evaluations/{assessment_session_id}/result",
    response_model=schemas.DailyEvaluationResultResponse,
)
def get_daily_evaluation_result(
    assessment_session_id: UUID,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.DailyEvaluationResultResponse:
    result = service.get_daily_evaluation_result(
        session,
        user=account,
        assessment_session_id=assessment_session_id,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily evaluation was not found.",
        )
    return result
