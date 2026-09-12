from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import (
    get_emission_calculation_service,
    get_emission_factor_service,
    get_factory_service,
)
from app.db.base import Base
from app.main import app
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.emission_factor_service import EmissionFactorService


def test_factor_and_calculation_api_round_trip() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def factor_override():
        session = session_factory()
        try:
            yield EmissionFactorService(session)
        finally:
            session.close()

    def factory_override():
        session = session_factory()
        try:
            from app.services.factory_service import FactoryService

            yield FactoryService(session)
        finally:
            session.close()

    def calculation_override():
        session = session_factory()
        try:
            yield EmissionCalculationService(session)
        finally:
            session.close()

    app.dependency_overrides[get_emission_factor_service] = factor_override
    app.dependency_overrides[get_emission_calculation_service] = calculation_override
    app.dependency_overrides[get_factory_service] = factory_override
    try:
        with TestClient(app) as client:
            factory = client.post(
                "/api/v1/factories",
                json={
                    "name": "Calculation Factory",
                    "industry_type": "Manufacturing",
                    "location": "Ahmedabad",
                    "production_unit": "units",
                },
            ).json()
            period = client.post(
                f"/api/v1/factories/{factory['id']}/periods",
                json={
                    "period_start": "2026-09-01",
                    "period_end": "2026-09-30",
                    "production_quantity": 100,
                    "production_unit": "units",
                },
            ).json()
            client.post(
                "/api/v1/emission-factors",
                json={
                    "category": "energy",
                    "source": "grid electricity",
                    "unit": "kwh",
                    "kg_co2e_per_unit": "0.4",
                    "geography": "India",
                    "source_reference": "Demo factor",
                    "valid_from": "2026-01-01",
                    "version": "demo-1",
                },
            )
            client.post(
                f"/api/v1/factories/{factory['id']}/periods/{period['id']}/energy",
                json={"source": "grid electricity", "quantity": 100, "unit": "kWh"},
            )
            calculation = client.post(
                f"/api/v1/factories/{factory['id']}/periods/{period['id']}/calculate"
            )

            assert calculation.status_code == 200
            assert calculation.json()["total_kg_co2e"] == "40.000000"
            assert calculation.json()["breakdown"][0]["category"] == "energy"
    finally:
        app.dependency_overrides.pop(get_emission_factor_service, None)
        app.dependency_overrides.pop(get_emission_calculation_service, None)
        app.dependency_overrides.pop(get_factory_service, None)
