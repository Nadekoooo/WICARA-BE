from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.accounts.dependencies import get_current_account
from app.modules.accounts.models import UserAccount
from app.modules.accounts.schemas import AccountProfileResponse, LearnerProfileRead, UserAccountRead
from app.modules.accounts.service import get_learner_profile

router = APIRouter()


@router.get("/me", response_model=AccountProfileResponse)
def read_current_account_profile(
    account: UserAccount = Depends(get_current_account),
    session: Session = Depends(get_session),
) -> AccountProfileResponse:
    profile = get_learner_profile(session, account)
    return AccountProfileResponse(
        account=UserAccountRead.model_validate(account),
        profile=LearnerProfileRead.model_validate(profile) if profile else None,
        onboarding_completed=bool(profile and profile.onboarding_completed),
    )
