from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/tracks", response_model=schemas.TrackListResponse)
def list_tracks(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> schemas.TrackListResponse:
    return service.list_tracks(session, user=account)


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
    return service.get_or_create_daily_evaluation(session, user=account)


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
