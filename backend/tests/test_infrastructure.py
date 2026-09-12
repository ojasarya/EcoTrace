import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import check_database_connection, get_session_factory


def test_configuration_loads_environment_values(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "Test API")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost:5432/test")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173, http://localhost:3000")

    settings = Settings()

    assert settings.app_name == "Test API"
    assert settings.database_url.endswith("/test")
    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "http://localhost:3000",
    ]


def test_configuration_repr_does_not_expose_database_url() -> None:
    database_url = "postgresql+psycopg://user:password@localhost:5432/ecotrace"
    settings = Settings(DATABASE_URL=database_url)

    assert database_url not in repr(settings)
    assert "password" not in repr(settings)


def test_configuration_requires_database_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(_env_file=None)


def test_configuration_accepts_python_field_names() -> None:
    settings = Settings(database_url="sqlite:///:memory:")

    assert settings.database_url == "sqlite:///:memory:"


def test_session_factory_can_create_a_session() -> None:
    factory = get_session_factory(
        Settings(DATABASE_URL="sqlite:///:memory:")
    )

    session = factory()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_database_check_reports_unavailable_database() -> None:
    settings = Settings(
        DATABASE_URL=(
            "postgresql+psycopg://localhost:1/unavailable?connect_timeout=1"
        )
    )

    assert check_database_connection(settings) is False
