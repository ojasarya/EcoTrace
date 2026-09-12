from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.services.auth_service import AuthService


def test_auth_register_login_and_token(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        service = AuthService(session)
        user = service.register("User@Example.com", "correct horse battery")
        assert user.email == "user@example.com"
        assert service.login("USER@example.com", "correct horse battery") is not None
        assert service.login("user@example.com", "wrong password") is None
        assert service.token_for(user)
        assert service.user_from_token(service.token_for(user)).id == user.id
        assert service.user_from_token("not-a-token") is None
