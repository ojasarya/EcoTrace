from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models.calculation import EmissionCalculation
from app.db.models.factory import Factory, ReportingPeriod
from app.db.models.intervention import Intervention
from app.services.roadmap_action_service import RoadmapActionService


def test_roadmap_action_can_be_created_and_updated() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        factory = Factory(name="F", industry_type="M", location="P", production_unit="u")
        period = ReportingPeriod(
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
            production_quantity=1,
            production_unit="u",
        )
        period.calculations.append(
            EmissionCalculation(total_kg_co2e=Decimal("10"), calculation_version="1")
        )
        factory.reporting_periods.append(period)
        intervention = Intervention(
            name="Action",
            category="energy",
            target_source="grid",
            description="Do it",
            estimated_cost=Decimal("100"),
            estimated_reduction_percentage=Decimal("20"),
            feasibility="high",
            urgency="high",
        )
        session.add_all([factory, intervention])
        session.commit()
        action = RoadmapActionService(session).create_action(
            factory.id,
            calculation_id=period.calculations[0].id,
            intervention_id=intervention.id,
            owner="Ops",
        )
        assert action.status == "planned"
        updated = RoadmapActionService(session).update_action(
            action, status="completed", actual_cost=Decimal("90")
        )
        assert updated.status == "completed"
        assert updated.actual_cost == Decimal("90")
