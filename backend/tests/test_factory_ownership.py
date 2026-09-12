from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

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
