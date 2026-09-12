from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import (
    get_emission_calculation_service,
    get_hotspot_service,
)
from app.db.base import Base
from app.db.models.calculation import EmissionBreakdown, EmissionCalculation
from app.db.models.factory import Factory, ReportingPeriod
from app.main import app
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.hotspot_service import HotspotService


def test_hotspot_api_returns_ranked_calculation_sources() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    with Session(engine) as session:
        factory = Factory(
            name="Hotspot Factory",
            industry_type="Manufacturing",
            location="Ahmedabad",
            production_unit="units",
        )
        period = ReportingPeriod(
            period_start=date(2026, 9, 1),
            period_end=date(2026, 9, 30),
            production_quantity=100,
            production_unit="units",
        )
        calculation = EmissionCalculation(
            total_kg_co2e=Decimal("100"),
            calculation_version="1.0",
        )
        calculation.breakdown = [
            EmissionBreakdown(
                category="energy",
                source="grid",
                activity_quantity=Decimal("100"),
                activity_unit="kwh",
                applied_factor=Decimal("0.7"),
                kg_co2e=Decimal("70"),
                percentage_of_total=Decimal("70"),
            ),
            EmissionBreakdown(
                category="waste",
                source="landfill",
                activity_quantity=Decimal("1"),
                activity_unit="tonne",
                applied_factor=Decimal("30"),
                kg_co2e=Decimal("30"),
                percentage_of_total=Decimal("30"),
            ),
        ]
        period.calculations.append(calculation)
        factory.reporting_periods.append(period)
        session.add(factory)
        session.commit()
        calculation_id = calculation.id

    def calculation_override():
        session = session_factory()
        try:
            yield EmissionCalculationService(session)
        finally:
            session.close()

    def hotspot_override():
        session = session_factory()
        try:
            yield HotspotService(EmissionCalculationService(session))
        finally:
            session.close()

    app.dependency_overrides[get_emission_calculation_service] = calculation_override
    app.dependency_overrides[get_hotspot_service] = hotspot_override
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/calculations/{calculation_id}/hotspots")
            assert response.status_code == 200
            assert response.json()[0]["source"] == "grid"
            assert response.json()[0]["severity"] == "high"

            missing = client.get("/api/v1/calculations/9999/hotspots")
            assert missing.status_code == 404
    finally:
        app.dependency_overrides.pop(get_emission_calculation_service, None)
        app.dependency_overrides.pop(get_hotspot_service, None)
