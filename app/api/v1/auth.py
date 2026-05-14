from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.modules.accounts.schemas import (
    AuthSessionResponse,
    GoogleSignInRequest,
    PasswordSignInRequest,
    SupabaseAuthRequest,
    UserAccountRead,
)
from app.modules.accounts.service import sync_supabase_user
from app.modules.accounts.supabase import (
    SupabaseTokenError,
    sign_in_with_google_id_token,
    sign_in_with_password,
    verify_supabase_access_token,
)

router = APIRouter(prefix="/auth")


@router.post("/supabase", response_model=AuthSessionResponse)
def authenticate_with_supabase(
    payload: SupabaseAuthRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    claims = _verified_claims(payload.access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return AuthSessionResponse(
        user_id=str(account.id),
        display_name=account.display_name,
        role=account.role,
        token=payload.access_token,
        email=account.email,
    )


@router.post("/sign-in", response_model=AuthSessionResponse)
async def sign_in_with_backend(
    payload: PasswordSignInRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    try:
        access_token = await sign_in_with_password(
            settings=settings,
            email_or_phone=payload.email_or_phone,
            password=payload.password,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    claims = _verified_claims(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return AuthSessionResponse(
        user_id=str(account.id),
        display_name=account.display_name,
        role=account.role,
        token=access_token,
        email=account.email,
    )


@router.post("/google", response_model=AuthSessionResponse)
async def sign_in_with_google(
    payload: GoogleSignInRequest,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthSessionResponse:
    try:
        access_token = await sign_in_with_google_id_token(
            settings=settings,
            id_token=payload.id_token,
            access_token=payload.access_token,
        )
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    claims = _verified_claims(access_token, settings)
    account = sync_supabase_user(session, claims=claims, role=payload.role)
    return AuthSessionResponse(
        user_id=str(account.id),
        display_name=account.display_name,
        role=account.role,
        token=access_token,
        email=account.email,
    )


@router.get("/me", response_model=UserAccountRead)
def current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> UserAccountRead:
    token = _bearer_token(authorization)
    claims = _verified_claims(token, settings)
    account = sync_supabase_user(session, claims=claims, role="learner")
    return UserAccountRead.model_validate(account)


def _verified_claims(token: str, settings: Settings) -> dict:
    try:
        return verify_supabase_access_token(token, settings)
    except SupabaseTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.strip()
