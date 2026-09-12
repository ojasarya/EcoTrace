from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.api.dependencies import get_auth_service, get_optional_current_user
from app.db.base import Base
from app.main import app
from app.services.auth_service import AuthService


def test_auth_api_register_login_and_current_user(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def override_service():
        session = sessions()
        try:
            yield AuthService(session)
        finally:
            session.close()

    app.dependency_overrides[get_auth_service] = override_service
    try:
        with TestClient(app) as client:
            registration = client.post(
                "/api/v1/auth/register",
                json={"email": "Operator@example.com", "password": "secure password"},
            )
            assert registration.status_code == 201
            assert (
                client.post(
                    "/api/v1/auth/register",
                    json={"email": "operator@example.com", "password": "secure password"},
                ).status_code
                == 409
            )
            login = client.post(
                "/api/v1/auth/login",
                json={"email": "OPERATOR@example.com", "password": "secure password"},
            )
            assert login.status_code == 200
            token = login.json()["access_token"]
            assert client.get("/api/v1/auth/me").status_code == 401
            profile = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert profile.status_code == 200
            assert profile.json()["email"] == "operator@example.com"
            assert (
                client.post(
                    "/api/v1/auth/login",
                    json={"email": "operator@example.com", "password": "wrong password"},
                ).status_code
                == 401
            )
    finally:
        app.dependency_overrides.pop(get_auth_service, None)


def test_optional_user_does_not_open_database_without_credentials(monkeypatch) -> None:
    def fail_if_database_is_open():
        raise AssertionError("database should not be opened")

    monkeypatch.setattr("app.api.dependencies.get_db", fail_if_database_is_open)
    assert get_optional_current_user(None) is None
