from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import (
    get_emission_calculation_service,
    get_emission_factor_service,
    get_factory_service,
    get_optional_current_user,
)
from app.db.base import Base
from app.db.models.calculation import EmissionCalculation
from app.db.models.factory import Factory, ReportingPeriod
from app.db.models.user import User
from app.main import app
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.emission_factor_service import EmissionFactorService
from app.services.factory_service import FactoryService


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


def test_emission_calculations_require_factory_owner_access() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    owner = User(email="owner@example.com", password_hash="hash")
    other_user = User(email="other@example.com", password_hash="hash")
    session.add_all([owner, other_user])
    session.flush()
    factory = Factory(
        name="Owned Calculation Factory",
        industry_type="Manufacturing",
        location="Pune",
        production_unit="units",
        owner_id=owner.id,
    )
    session.add(factory)
    session.flush()
    period = ReportingPeriod(
        factory_id=factory.id,
        period_start=date(2026, 9, 1),
        period_end=date(2026, 9, 30),
        production_quantity=100,
        production_unit="units",
    )
    session.add(period)
    session.flush()
    calculation = EmissionCalculation(
        reporting_period_id=period.id,
        total_kg_co2e=100,
        calculation_version="1.0",
        status="completed",
    )
    session.add(calculation)
    session.commit()

    def calculation_override():
        yield EmissionCalculationService(session)

    app.dependency_overrides[get_emission_calculation_service] = calculation_override
    try:
        with TestClient(app) as client:
            app.dependency_overrides[get_optional_current_user] = lambda: None
            assert (
                client.get(f"/api/v1/factories/{factory.id}/calculations").status_code
                == 401
            )

            app.dependency_overrides[get_optional_current_user] = lambda: other_user
            assert (
                client.get(f"/api/v1/factories/{factory.id}/calculations").status_code
                == 403
            )

            app.dependency_overrides[get_optional_current_user] = lambda: owner
            response = client.get(f"/api/v1/factories/{factory.id}/calculations")
            assert response.status_code == 200
            assert response.json()[0]["id"] == calculation.id
    finally:
        app.dependency_overrides.pop(get_emission_calculation_service, None)
        app.dependency_overrides.pop(get_optional_current_user, None)
        session.close()
