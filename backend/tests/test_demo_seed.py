from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.calculation import EmissionCalculation
from app.db.models.factory import Factory
from app.db.models.intervention import Intervention
from app.services.demo_seed_service import seed_demo_data


def test_demo_seed_creates_calculation_and_is_idempotent() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        first = seed_demo_data(session)
        second = seed_demo_data(session)
        assert first.id == second.id
        assert len(session.scalars(select(Factory)).all()) == 1
        assert len(session.scalars(select(Intervention)).all()) == 3
        calculation = session.scalar(select(EmissionCalculation))
        assert calculation is not None
        assert calculation.total_kg_co2e == 8150
