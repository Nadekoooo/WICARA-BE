from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "WICARA_GEMINI_API_KEY"),
    )
    gemini_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta",
        validation_alias=AliasChoices("GEMINI_BASE_URL", "WICARA_GEMINI_BASE_URL"),
    )
    ai_request_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        validation_alias=AliasChoices(
            "AI_REQUEST_TIMEOUT_SECONDS",
            "WICARA_AI_REQUEST_TIMEOUT_SECONDS",
        ),
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()
