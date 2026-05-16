from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_AI_PROVIDER = "gemini"
DEFAULT_AI_MODEL = "gemini-2.5-flash"


class AISettings(BaseSettings):
    ai_provider: str = Field(
        default=DEFAULT_AI_PROVIDER,
        validation_alias=AliasChoices("AI_PROVIDER", "WICARA_AI_PROVIDER"),
    )
    ai_model: str = Field(
        default=DEFAULT_AI_MODEL,
        validation_alias=AliasChoices("AI_MODEL", "WICARA_AI_MODEL"),
    )
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


@lru_cache
def get_ai_settings() -> AISettings:
    return AISettings()
