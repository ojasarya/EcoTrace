"""FastAPI dependency providers."""

from collections.abc import Generator

from app.db.session import get_db
from app.services.factory_service import FactoryService
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.emission_factor_service import EmissionFactorService
from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService
from app.services.simulation_service import SimulationService
from app.services.roadmap_service import RoadmapService


def get_factory_service() -> Generator[FactoryService, None, None]:
    for session in get_db():
        yield FactoryService(session)


def get_emission_factor_service() -> Generator[EmissionFactorService, None, None]:
    for session in get_db():
        yield EmissionFactorService(session)


def get_emission_calculation_service() -> Generator[EmissionCalculationService, None, None]:
    for session in get_db():
        yield EmissionCalculationService(session)


def get_hotspot_service() -> Generator[HotspotService, None, None]:
    for session in get_db():
        yield HotspotService(EmissionCalculationService(session))


def get_intervention_service() -> Generator[InterventionService, None, None]:
    for session in get_db():
        yield InterventionService(session)


def get_simulation_service() -> Generator[SimulationService, None, None]:
    for session in get_db():
        yield SimulationService(EmissionCalculationService(session))


def get_roadmap_service() -> Generator[RoadmapService, None, None]:
    for session in get_db():
        calculation_service = EmissionCalculationService(session)
        yield RoadmapService(
        HotspotService(calculation_service),
        InterventionService(session),
        )
