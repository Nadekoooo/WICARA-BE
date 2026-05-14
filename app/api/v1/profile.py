from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.accounts.schemas import (
    LearnerProfileOnboardingRequest,
    LearnerProfileRead,
)
from app.modules.accounts.service import get_learner_profile, save_onboarding_profile

router = APIRouter(prefix="/me/profile")


@router.get("", response_model=LearnerProfileRead)
def read_profile(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> LearnerProfileRead:
    profile = get_learner_profile(session, account)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile was not found.",
        )
    return LearnerProfileRead.model_validate(profile)


@router.put("/onboarding", response_model=LearnerProfileRead)
def save_onboarding(
    payload: LearnerProfileOnboardingRequest,
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> LearnerProfileRead:
    profile = save_onboarding_profile(session, user=account, payload=payload)
    return LearnerProfileRead.model_validate(profile)
