from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.api.dependencies import get_factory_service, get_optional_current_user
from app.main import app
from app.db.base import Base
from app.db.models.factory import Factory
from app.db.models.user import User
from app.services.factory_service import FactoryService


def test_factory_can_be_linked_to_authenticated_owner() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(email="owner@example.com", password_hash="hash")
        session.add(user)
        session.flush()
        factory = FactoryService(session).create_factory(
            name="Owned",
            industry_type="Manufacturing",
            location="Pune",
            production_unit="units",
            owner_id=user.id,
        )
        assert factory.owner_id == user.id
        assert FactoryService(session).list_factories_for_owner(user.id) == [factory]
        assert FactoryService(session).list_accessible_factories(None) == []
        assert FactoryService(session).list_accessible_factories(user.id) == [factory]


def test_owned_factory_requires_matching_user() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        owner = User(email="owner@example.com", password_hash="hash")
        other_user = User(email="other@example.com", password_hash="hash")
        session.add_all([owner, other_user])
        session.flush()
        factory = FactoryService(session).create_factory(
            name="Owned",
            industry_type="Manufacturing",
            location="Pune",
            production_unit="units",
            owner_id=owner.id,
        )

        def override_factory_service():
            yield FactoryService(session)

        app.dependency_overrides[get_factory_service] = override_factory_service
        try:
            with TestClient(app) as client:
                app.dependency_overrides[get_optional_current_user] = lambda: None
                assert client.get(f"/api/v1/factories/{factory.id}").status_code == 401

                app.dependency_overrides[get_optional_current_user] = lambda: other_user
                assert client.get(f"/api/v1/factories/{factory.id}").status_code == 403

                app.dependency_overrides[get_optional_current_user] = lambda: owner
                response = client.get(f"/api/v1/factories/{factory.id}")
                assert response.status_code == 200
                assert response.json()["id"] == factory.id
        finally:
            app.dependency_overrides.pop(get_factory_service, None)
            app.dependency_overrides.pop(get_optional_current_user, None)
