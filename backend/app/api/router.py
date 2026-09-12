"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes import auth, emissions, factories, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(factories.router)
api_router.include_router(emissions.router)
