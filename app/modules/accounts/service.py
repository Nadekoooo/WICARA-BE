from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounts.models import UserAccount


def sync_supabase_user(
    session: Session,
    *,
    claims: dict[str, Any],
    role: str,
) -> UserAccount:
    supabase_user_id = str(claims["sub"])
    email = _string_or_none(claims.get("email"))
    phone = _string_or_none(claims.get("phone"))
    metadata = _metadata(claims)
    display_name = _display_name(metadata, email, phone)

    account = session.scalar(
        select(UserAccount).where(UserAccount.supabase_user_id == supabase_user_id)
    )
    if account is None:
        account = UserAccount(
            supabase_user_id=supabase_user_id,
            provider_subject=supabase_user_id,
        )
        session.add(account)

    account.email = email
    account.phone = phone
    account.display_name = display_name
    account.role = _normalize_role(role)
    account.auth_provider = str(claims.get("app_metadata", {}).get("provider") or "supabase")
    account.status = "active"
    account.metadata_json = {
        "app_metadata": claims.get("app_metadata", {}),
        "user_metadata": metadata,
    }
    account.last_seen_at = datetime.now(UTC)
    session.commit()
    session.refresh(account)
    return account


def _normalize_role(role: str) -> str:
    cleaned = role.strip().lower()
    return cleaned if cleaned in {"learner"} else "learner"


def _metadata(claims: dict[str, Any]) -> dict[str, Any]:
    value = claims.get("user_metadata") or claims.get("raw_user_meta_data") or {}
    return value if isinstance(value, dict) else {}


def _display_name(
    metadata: dict[str, Any],
    email: str | None,
    phone: str | None,
) -> str:
    for key in ("full_name", "name", "display_name"):
        value = _string_or_none(metadata.get(key))
        if value:
            return value
    return email or phone or "Learner"


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
