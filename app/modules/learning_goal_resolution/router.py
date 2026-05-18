from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.learning_goal_resolution.schemas import (
    ActiveLearningGoalResponse,
    CreateLearningGoalFromConceptRequest,
    PathSelectionRequest,
    RepromptLearningGoalRequest,
    ResolveLearningGoalRequest,
    SessionGoalHistoryResponse,
    SelectResolvedConceptRequest,
)
from app.modules.learning_goal_resolution.service import (
    ActiveLearningGoalExists,
    GoalResolverService,
)

router = APIRouter()
service = GoalResolverService()


def _active_goal_conflict(exc: ActiveLearningGoalExists) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": "ACTIVE_LEARNING_GOAL_EXISTS",
            "message": "You already have an active session goal for this node.",
            "active_goal": exc.active_goal.model_dump(mode="json"),
        },
    )


@router.post("/learning-goals/resolve")
async def resolve_learning_goal(
    payload: ResolveLearningGoalRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    return await service.resolve(
        session,
        user=user,
        raw_query=payload.raw_query,
        subject_code=payload.subject_code,
        education_level=payload.education_level,
        grade_level=payload.grade_level,
        language=payload.language,
    )


@router.post("/learning-goals/resolve/{resolution_id}/confirm")
def confirm_learning_goal(
    resolution_id: UUID,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.confirm(session, user=user, resolution_id=resolution_id)
    except ActiveLearningGoalExists as exc:
        raise _active_goal_conflict(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found.")
    return result


@router.post("/learning-goals/resolve/{resolution_id}/reprompt")
async def reprompt_learning_goal(
    resolution_id: UUID,
    payload: RepromptLearningGoalRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    result = await service.reprompt(
        session,
        user=user,
        resolution_id=resolution_id,
        raw_query=payload.raw_query,
    )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found.")
    return result


@router.post("/learning-goals/resolve/{resolution_id}/select")
def select_resolved_concept(
    resolution_id: UUID,
    payload: SelectResolvedConceptRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.select_concept(
            session,
            user=user,
            resolution_id=resolution_id,
            concept_id=payload.concept_id,
            concept_code=payload.concept_code,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resolution not found.")
    return result


@router.get("/learning-goals/active")
def get_active_learning_goal(
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
) -> ActiveLearningGoalResponse:
    return service.get_active_goal(session, user=user)


@router.get("/learning-goals/history", response_model=SessionGoalHistoryResponse)
def get_session_goal_history(
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
) -> SessionGoalHistoryResponse:
    return service.list_session_goal_history(session, user=user)


@router.post("/learning-goals/from-concept")
def create_learning_goal_from_concept(
    payload: CreateLearningGoalFromConceptRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        return service.create_from_concept(
            session,
            user=user,
            concept_id=payload.concept_id,
            concept_code=payload.concept_code,
            subject_code=payload.subject_code,
            language=payload.language,
        )
    except ActiveLearningGoalExists as exc:
        raise _active_goal_conflict(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/learning-goals/{learning_goal_id}/cancel")
def cancel_learning_goal(
    learning_goal_id: UUID,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    result = service.cancel_goal(session, user=user, learning_goal_id=learning_goal_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found.")
    return result


@router.post("/learning-goals/{learning_goal_id}/archive")
def archive_learning_goal(
    learning_goal_id: UUID,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.archive_goal(session, user=user, learning_goal_id=learning_goal_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found.")
    return result


@router.post("/learning-goals/{learning_goal_id}/path-selection")
def select_learning_path(
    learning_goal_id: UUID,
    payload: PathSelectionRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.track_builder.select_path(
            session,
            user=user,
            learning_goal_id=learning_goal_id,
            path_option=payload.path_option,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal not found.")
    return result


@router.get("/materials/search")
def search_materials(
    q: str = Query(..., min_length=1),
    subject_code: str | None = None,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    return {"items": service.search_materials(session, query=q, subject_code=subject_code, user=user)}
