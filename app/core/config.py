from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "WICARA Backend"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://wicara:wicara@localhost:5432/wicara"
    cors_allow_origins: list[str] = [
        "http://localhost",
        "http://localhost:*",
        "http://127.0.0.1",
        "http://127.0.0.1:*",
    ]

    model_config = SettingsConfigDict(env_prefix="WICARA_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
