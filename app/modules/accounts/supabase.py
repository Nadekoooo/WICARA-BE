from __future__ import annotations

from functools import lru_cache
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from app.core.config import Settings


class SupabaseTokenError(ValueError):
    pass


@lru_cache
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def verify_supabase_access_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        signing_key = _jwks_client(settings.supabase_jwks_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=settings.supabase_jwt_audience,
            issuer=settings.supabase_issuer,
            options={"require": ["sub", "iss", "aud", "exp"]},
        )
    except jwt.PyJWTError as exc:
        raise SupabaseTokenError("Invalid Supabase access token.") from exc


async def sign_in_with_password(
    *,
    settings: Settings,
    email_or_phone: str,
    password: str,
) -> str:
    if not settings.supabase_anon_key:
        raise SupabaseTokenError("SUPABASE_ANON_KEY is missing on backend.")
    payload = {"password": password}
    if "@" in email_or_phone:
        payload["email"] = email_or_phone.strip()
    else:
        payload["phone"] = email_or_phone.strip()
    return await _token_exchange(
        settings=settings,
        grant_type="password",
        payload=payload,
    )


async def register_with_password(
    *,
    settings: Settings,
    email: str,
    password: str,
    display_name: str,
) -> str:
    if not settings.supabase_anon_key:
        raise SupabaseTokenError("SUPABASE_ANON_KEY is missing on backend.")
    signup_url = f"{settings.supabase_project_url.rstrip('/')}/auth/v1/signup"
    headers = {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }
    payload = {
        "email": email.strip(),
        "password": password,
        "data": {"display_name": display_name.strip()},
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(signup_url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise SupabaseTokenError(_supabase_error_message(response))
        data = response.json()
        access_token = str(data.get("access_token") or "").strip()
        if not access_token:
            raise SupabaseTokenError(
                "Registration succeeded, but email confirmation is required before login."
            )
        return access_token
    except httpx.HTTPError as exc:
        raise SupabaseTokenError(f"Supabase auth request failed: {exc}") from exc


async def sign_in_with_google_id_token(
    *,
    settings: Settings,
    id_token: str,
    access_token: str | None = None,
    nonce: str | None = None,
) -> str:
    if not settings.supabase_anon_key:
        raise SupabaseTokenError("SUPABASE_ANON_KEY is missing on backend.")
    payload: dict[str, str] = {
        "provider": "google",
        "id_token": id_token,
    }
    if access_token:
        payload["access_token"] = access_token
    if nonce:
        payload["nonce"] = nonce
    return await _token_exchange(
        settings=settings,
        grant_type="id_token",
        payload=payload,
    )


async def _token_exchange(
    *,
    settings: Settings,
    grant_type: str,
    payload: dict[str, str],
) -> str:
    token_url = f"{settings.supabase_project_url.rstrip('/')}/auth/v1/token"
    headers = {
        "apikey": settings.supabase_anon_key,
        "Content-Type": "application/json",
    }
    params = {"grant_type": grant_type}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(token_url, params=params, headers=headers, json=payload)
        if response.status_code >= 400:
            raise SupabaseTokenError(_supabase_error_message(response))
        data = response.json()
        access_token = str(data.get("access_token") or "").strip()
        if not access_token:
            raise SupabaseTokenError("Supabase auth response has no access_token.")
        return access_token
    except httpx.HTTPError as exc:
        raise SupabaseTokenError(f"Supabase auth request failed: {exc}") from exc


def _supabase_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return f"Supabase auth failed with status {response.status_code}."
    for key in ("msg", "message", "error_description", "error"):
        value = data.get(key)
        if value:
            return str(value)
    return f"Supabase auth failed with status {response.status_code}."
