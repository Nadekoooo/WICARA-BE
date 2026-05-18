from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.posttests.schemas import PosttestStartRequest, PosttestSubmitAnswerRequest
from app.modules.posttests.service import AdaptivePosttestService, DuplicateQuestionAttempt

router = APIRouter()
service = AdaptivePosttestService()


@router.post("/posttests/start")
def start_posttest(
    payload: PosttestStartRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.start(
            session,
            user=user,
            learning_goal_id=payload.learning_goal_id,
            track_id=payload.track_id,
            module_id=payload.module_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning goal or track not found.")
    return result


@router.get("/posttests/{session_id}")
def read_posttest(
    session_id: UUID,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    result = service.read(session, user=user, session_id=session_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posttest session not found.")
    return result


@router.post("/posttests/{session_id}/answers")
def submit_posttest_answer(
    session_id: UUID,
    payload: PosttestSubmitAnswerRequest,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    try:
        result = service.submit_answer(
            session,
            user=user,
            session_id=session_id,
            question_id=payload.question_id,
            selected_option_id=payload.selected_option_id,
            confidence=payload.confidence,
        )
    except DuplicateQuestionAttempt as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "QUESTION_ALREADY_ANSWERED", "message": "This question already has an answer."},
        ) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posttest session not found.")
    return result


@router.post("/posttests/{session_id}/finalize")
def finalize_posttest(
    session_id: UUID,
    session: Session = Depends(get_session),
    user: UserAccount = Depends(get_current_account),
):
    result = service.finalize(session, user=user, session_id=session_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Posttest session not found.")
    return result
