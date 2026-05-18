from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _engine_connect_args(database_url: str) -> dict[str, object]:
    """
    Supabase transaction pooler (port 6543) can break with psycopg prepared statements.
    Disable them when connecting through Supabase pooler hosts.
    """
    try:
        url = make_url(database_url)
    except Exception:
        return {}

    backend = url.get_backend_name()
    driver = url.get_driver_name()
    host = (url.host or "").lower()
    if backend == "postgresql" and driver == "psycopg" and "pooler.supabase.com" in host:
        return {"prepare_threshold": None}
    return {}


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=_engine_connect_args(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
