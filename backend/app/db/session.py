"""SQLAlchemy engine and session dependency foundation."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db import models  # noqa: F401
from app.db.base import Base


@lru_cache
def get_engine(database_url: str) -> Engine:
    """Create one SQLAlchemy engine for the configured database URL."""

    return create_engine(database_url, pool_pre_ping=True)


def get_session_factory(
    settings: Settings | None = None,
) -> sessionmaker[Session]:
    """Create a session factory for dependency injection."""

    configured = settings or get_settings()
    return sessionmaker(
        bind=get_engine(configured.database_url),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it after request handling."""

    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def check_database_connection(settings: Settings | None = None) -> bool:
    """Return whether the configured database accepts a simple query."""

    configured = settings or get_settings()
    try:
        with get_engine(configured.database_url).connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return False
    return True
