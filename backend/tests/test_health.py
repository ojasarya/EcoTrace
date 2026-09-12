from fastapi.testclient import TestClient

from app.api.routes import health as health_routes
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ecotrace-api"}


def test_frontend_origin_is_allowed_by_cors() -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_database_health_reports_available(monkeypatch) -> None:
    monkeypatch.setattr(health_routes, "check_database_connection", lambda: True)

    response = client.get("/api/v1/health/database")

    assert response.status_code == 200
    assert response.json()["database"] == "available"


def test_database_health_reports_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(health_routes, "check_database_connection", lambda: False)

    response = client.get("/api/v1/health/database")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"
