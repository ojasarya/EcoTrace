"""Health and service status endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic application health status."""

    return {"status": "ok", "service": "ecotrace-api"}
