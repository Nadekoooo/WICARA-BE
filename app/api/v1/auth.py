from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.modules.accounts.dependencies import (
    bearer_token,
    verify_supabase_token_or_401,
)
from app.modules.accounts.schemas import (
    AuthSessionResponse,
    GoogleSignInRequest,
    PasswordRegisterRequest,
    PasswordSignInRequest,
    SupabaseAuthRequest,
    UserAccountRead,
)
from app.modules.accounts.models import UserAccount
from app.modules.accounts.service import get_learner_profile, sync_supabase_user
from app.modules.accounts.supabase import (
    SupabaseTokenError,
    refresh_access_token,
    register_with_password,
    sign_in_with_google_id_token,
    sign_in_with_password,
)

router = APIRouter(prefix="/auth")


def _auth_session_response(
    session: Session,
    *,
    account: UserAccount,
    token: str,
    refresh_token: str = "",
) -> AuthSessionResponse:
    profile = get_learner_profile(session, account)
    return AuthSessionResponse(
        user_id=str(account.id),
        display_name=account.display_name,
        role=account.role,
        token=token,
        refresh_token=refresh_token,
        email=account.email,
        onboarding_completed=bool(profile and profile.onboarding_completed),
    )


@router.post("/supabase", response_model=AuthSessionResponse)
def authenticate_with_supabase(
    payload: SupabaseAuthRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    claims = verify_supabase_token_or_401(payload.access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return _auth_session_response(session, account=account, token=payload.access_token)


@router.post("/sign-in", response_model=AuthSessionResponse)
async def sign_in_with_backend(
    payload: PasswordSignInRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    try:
        access_token, supabase_refresh_token = await sign_in_with_password(
            settings=settings,
            email_or_phone=payload.email_or_phone,
            password=payload.password,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    claims = verify_supabase_token_or_401(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return _auth_session_response(
        session, account=account, token=access_token, refresh_token=supabase_refresh_token
    )


@router.post("/register", response_model=AuthSessionResponse)
async def register_with_backend(
    payload: PasswordRegisterRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    try:
        access_token, supabase_refresh_token = await register_with_password(
            settings=settings,
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    claims = verify_supabase_token_or_401(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return _auth_session_response(
        session, account=account, token=access_token, refresh_token=supabase_refresh_token
    )


@router.post("/google", response_model=AuthSessionResponse)
async def sign_in_with_google(
    payload: GoogleSignInRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    try:
        access_token, supabase_refresh_token = await sign_in_with_google_id_token(
            settings=settings,
            id_token=payload.id_token,
            access_token=payload.access_token,
            nonce=payload.nonce,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    claims = verify_supabase_token_or_401(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return _auth_session_response(
        session, account=account, token=access_token, refresh_token=supabase_refresh_token
    )


class _RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=AuthSessionResponse)
async def refresh_session(
    payload: _RefreshRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    """Exchange a Supabase refresh_token for a new access_token + refresh_token pair."""
    try:
        access_token, new_refresh_token = await refresh_access_token(
            settings=settings,
            refresh_token=payload.refresh_token,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    claims = verify_supabase_token_or_401(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role="learner")
    return _auth_session_response(
        session, account=account, token=access_token, refresh_token=new_refresh_token
    )


@router.get("/me", response_model=UserAccountRead)
def current_user(
    token: str = Depends(bearer_token),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UserAccountRead:
    claims = verify_supabase_token_or_401(token, settings)
    account = sync_supabase_user(session, claims=claims, role="learner")
    return UserAccountRead.model_validate(account)
