from functools import lru_cache
from urllib.parse import quote

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "WICARA Backend"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://wicara:wicara@localhost:5432/wicara",
        validation_alias=AliasChoices("WICARA_DATABASE_URL", "DATABASE_URL"),
    )
    supabase_project_url: str = Field(
        default="https://gwbqhirtkgkghnpahtgt.supabase.co",
        validation_alias=AliasChoices("WICARA_SUPABASE_PROJECT_URL", "SUPABASE_PROJECT_URL"),
    )
    supabase_jwks_url: str = Field(
        default="https://gwbqhirtkgkghnpahtgt.supabase.co/auth/v1/.well-known/jwks.json",
        validation_alias=AliasChoices("WICARA_SUPABASE_JWKS_URL", "SUPABASE_JWKS_URL"),
    )
    supabase_issuer: str = Field(
        default="https://gwbqhirtkgkghnpahtgt.supabase.co/auth/v1",
        validation_alias=AliasChoices("WICARA_SUPABASE_ISSUER", "SUPABASE_ISSUER"),
    )
    supabase_jwt_audience: str = Field(
        default="authenticated",
        validation_alias=AliasChoices("WICARA_SUPABASE_JWT_AUDIENCE", "SUPABASE_JWT_AUDIENCE"),
    )
    supabase_anon_key: str = Field(
        default="",
        validation_alias=AliasChoices("WICARA_SUPABASE_ANON_KEY", "SUPABASE_ANON_KEY"),
    )
    cors_allow_origins: list[str] = [
        "http://localhost",
        "http://localhost:*",
        "http://127.0.0.1",
        "http://127.0.0.1:*",
    ]

    model_config = SettingsConfigDict(env_prefix="WICARA_", env_file=".env", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        text = str(value).strip().strip('"').strip("'")
        if text.startswith("DATABASE_URL="):
            text = text.removeprefix("DATABASE_URL=").strip().strip('"').strip("'")
        text = _quote_database_credentials(text)
        if text.startswith("postgresql://"):
            text = text.replace("postgresql://", "postgresql+psycopg://", 1)
        return text


def _quote_database_credentials(url: str) -> str:
    scheme_separator = "://"
    if scheme_separator not in url:
        return url
    scheme, remainder = url.split(scheme_separator, 1)
    if "@" not in remainder:
        return url

    credentials, host_and_path = remainder.rsplit("@", 1)
    if ":" not in credentials:
        return url

    username, password = credentials.split(":", 1)
    safe_credentials = f"{quote(username, safe='')}:{quote(password, safe='')}"
    return f"{scheme}{scheme_separator}{safe_credentials}@{host_and_path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
