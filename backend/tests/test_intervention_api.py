from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_hotspot_service, get_intervention_service
from app.db.base import Base
from app.db.models.calculation import EmissionBreakdown, EmissionCalculation
from app.db.models.factory import Factory, ReportingPeriod
from app.main import app
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService


def test_intervention_matching_returns_explainable_recommendation() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with Session(engine) as session:
        factory = Factory(name="Factory", industry_type="Manufacturing", location="Pune", production_unit="units")
        period = ReportingPeriod(period_start=date(2026, 9, 1), period_end=date(2026, 9, 30), production_quantity=1, production_unit="units")
        calculation = EmissionCalculation(total_kg_co2e=Decimal("100"), calculation_version="1")
        calculation.breakdown = [EmissionBreakdown(category="energy", source="grid", activity_quantity=Decimal("1"), activity_unit="kwh", applied_factor=Decimal("100"), kg_co2e=Decimal("100"), percentage_of_total=Decimal("100"))]
        period.calculations.append(calculation)
        factory.reporting_periods.append(period)
        session.add(factory)
        session.commit()
        calculation_id = calculation.id

    def hotspot_override():
        session = session_factory()
        try:
            yield HotspotService(EmissionCalculationService(session))
        finally:
            session.close()

    def intervention_override():
        session = session_factory()
        try:
            yield InterventionService(session)
        finally:
            session.close()

    app.dependency_overrides[get_hotspot_service] = hotspot_override
    app.dependency_overrides[get_intervention_service] = intervention_override
    try:
        with TestClient(app) as client:
            client.post("/api/v1/interventions", json={
                "name": "Renewable electricity", "category": "energy", "target_source": "GRID",
                "description": "Replace grid power", "estimated_cost": "5000",
                "estimated_reduction_percentage": "40", "feasibility": "medium", "urgency": "high",
            })
            response = client.get(f"/api/v1/calculations/{calculation_id}/recommendations")
            assert response.status_code == 200
            assert response.json()[0]["name"] == "Renewable electricity"
            assert response.json()[0]["hotspot_rank"] == 1
            assert response.json()[0]["recommendation_rank"] == 1
            assert Decimal(response.json()[0]["estimated_reduction_kg_co2e"]) == Decimal("40")
    finally:
        app.dependency_overrides.pop(get_hotspot_service, None)
        app.dependency_overrides.pop(get_intervention_service, None)
