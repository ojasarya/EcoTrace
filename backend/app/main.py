"""FastAPI application entry point for EcoTrace."""

from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="EcoTrace API",
    description="Backend foundation for the EcoTrace industrial emissions platform.",
    version="0.1.0",
)

app.include_router(api_router)
