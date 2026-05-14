from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.modules.accounts import supabase


def test_google_id_token_exchange_forwards_nonce(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    token = "google-id-token"

    async def fake_token_exchange(**kwargs: object) -> str:
        captured.update(kwargs)
        return "supabase-access-token"

    monkeypatch.setattr(supabase, "_token_exchange", fake_token_exchange)

    access_token = asyncio.run(
        supabase.sign_in_with_google_id_token(
            settings=SimpleNamespace(supabase_anon_key="anon-key"),
            id_token=token,
            nonce="raw-nonce",
        )
    )

    assert access_token == "supabase-access-token"
    assert captured["grant_type"] == "id_token"
    assert captured["payload"] == {
        "provider": "google",
        "id_token": token,
        "nonce": "raw-nonce",
    }
