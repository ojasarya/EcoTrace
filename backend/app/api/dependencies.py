"""FastAPI dependency providers."""

from collections.abc import Generator

from app.db.session import get_db
from app.services.factory_service import FactoryService


def get_factory_service() -> Generator[FactoryService, None, None]:
    for session in get_db():
        yield FactoryService(session)
