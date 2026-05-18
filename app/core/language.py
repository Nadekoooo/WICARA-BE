from __future__ import annotations

from typing import Any

INDONESIAN_LANGUAGE_ALIASES = {
    "id",
    "id-id",
    "ind",
    "indo",
    "indonesian",
    "bahasa",
    "bahasa indonesia",
}
ENGLISH_LANGUAGE_ALIASES = {"en", "en-us", "en-gb", "eng", "english"}


def normalize_language_code(language: str | None, *, fallback: str = "en") -> str:
    normalized = str(language or "").strip().lower().replace("_", "-")
    if not normalized:
        return fallback
    if normalized in INDONESIAN_LANGUAGE_ALIASES or "indo" in normalized:
        return "id"
    if normalized in ENGLISH_LANGUAGE_ALIASES:
        return "en"
    return fallback


def is_indonesian_language(language: str | None) -> bool:
    return normalize_language_code(language) == "id"


def language_display_name(language: str | None) -> str:
    return "Indonesian" if is_indonesian_language(language) else "English"


def preferred_language_code(user: Any) -> str:
    profile = getattr(user, "learner_profile", None)
    preferred_language = getattr(profile, "preferred_language", None)
    return normalize_language_code(preferred_language)
