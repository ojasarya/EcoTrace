from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_factory_service
from app.db.base import Base
from app.main import app
from app.services.factory_service import FactoryService


def test_factory_and_activity_api_round_trip() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_service():
        session = session_factory()
        try:
            yield FactoryService(session)
        finally:
            session.close()

    app.dependency_overrides[get_factory_service] = override_service
    try:
        with TestClient(app) as client:
            factory_response = client.post(
                "/api/v1/factories",
                json={
                    "name": "Demo Factory",
                    "industry_type": "Manufacturing",
                    "location": "Ahmedabad",
                    "production_unit": "units",
                },
            )
            assert factory_response.status_code == 201
            factory_id = factory_response.json()["id"]

            period_response = client.post(
                f"/api/v1/factories/{factory_id}/periods",
                json={
                    "period_start": "2026-09-01",
                    "period_end": "2026-09-30",
                    "production_quantity": "24000",
                    "production_unit": "units",
                },
            )
            assert period_response.status_code == 201
            period_id = period_response.json()["id"]

            energy_response = client.post(
                f"/api/v1/factories/{factory_id}/periods/{period_id}/energy",
                json={
                    "source": "grid electricity",
                    "quantity": "24000",
                    "unit": "kWh",
                    "renewable_percentage": "20",
                },
            )
            assert energy_response.status_code == 201
            assert energy_response.json()["reporting_period_id"] == period_id

            listed = client.get(
                f"/api/v1/factories/{factory_id}/periods/{period_id}/energy"
            )
            assert listed.status_code == 200
            assert len(listed.json()) == 1
    finally:
        app.dependency_overrides.pop(get_factory_service, None)


def test_factory_api_validates_date_ranges_and_missing_resources() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_service():
        session = session_factory()
        try:
            yield FactoryService(session)
        finally:
            session.close()

    app.dependency_overrides[get_factory_service] = override_service
    try:
        with TestClient(app) as client:
            invalid_period = client.post(
                "/api/v1/factories/999/periods",
                json={
                    "period_start": "2026-09-30",
                    "period_end": "2026-09-01",
                    "production_quantity": 1,
                    "production_unit": "unit",
                },
            )
            assert invalid_period.status_code == 422

            missing_factory = client.get("/api/v1/factories/999")
            assert missing_factory.status_code == 404
    finally:
        app.dependency_overrides.pop(get_factory_service, None)
