"""Health and service status endpoints."""

from fastapi import APIRouter, HTTPException

from app.db.session import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic application health status."""

    return {"status": "ok", "service": "ecotrace-api"}


@router.get("/health/database")
def database_health_check() -> dict[str, str]:
    """Verify that the configured database accepts a simple query."""

    if not check_database_connection():
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "service": "ecotrace-api", "database": "available"}
