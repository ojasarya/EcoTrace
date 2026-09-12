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
from app.services.dashboard_service import DashboardService
from app.services.roadmap_action_service import RoadmapActionService
from app.services.anomaly_service import AnomalyService


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


def get_dashboard_service() -> Generator[DashboardService, None, None]:
    for session in get_db():
        calculation_service = EmissionCalculationService(session)
        hotspot_service = HotspotService(calculation_service)
        intervention_service = InterventionService(session)
        yield DashboardService(
        calculation_service,
        hotspot_service,
        intervention_service,
        RoadmapService(hotspot_service, intervention_service),
        )


def get_roadmap_action_service() -> Generator[RoadmapActionService, None, None]:
    for session in get_db():
        yield RoadmapActionService(session)


def get_anomaly_service() -> Generator[AnomalyService, None, None]:
    for session in get_db():
        yield AnomalyService(EmissionCalculationService(session))
