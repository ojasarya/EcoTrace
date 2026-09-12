"""Emission factor and calculation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.dependencies import (
    get_emission_calculation_service,
    get_emission_factor_service,
    get_hotspot_service,
    get_intervention_service,
    get_simulation_service,
    get_roadmap_service,
    get_dashboard_service,
    get_anomaly_service,
    get_report_service,
    get_optional_current_user,
)
from app.db.models.factory import Factory
from app.db.models.calculation import EmissionCalculation
from app.db.models.user import User
from app.db.models.factory import ReportingPeriod
from app.schemas.emission import (
    EmissionCalculationRead,
    EmissionFactorCreate,
    EmissionFactorRead,
)
from app.schemas.hotspot import HotspotRead
from app.schemas.intervention import (
    InterventionCreate,
    InterventionRead,
    RecommendationRead,
)
from app.schemas.simulation import SimulationRead, SimulationRequest
from app.schemas.roadmap import RoadmapRead
from app.schemas.dashboard import DashboardRead
from app.schemas.anomaly import AnomalyRead
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.emission_factor_service import EmissionFactorService
from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService
from app.services.simulation_service import SimulationService
from app.services.roadmap_service import RoadmapService
from app.services.dashboard_service import DashboardService
from app.services.anomaly_service import AnomalyService
from app.services.report_service import ReportService

router = APIRouter(tags=["emissions"])
FactorService = Annotated[
    EmissionFactorService,
    Depends(get_emission_factor_service),
]
CalculationService = Annotated[
    EmissionCalculationService,
    Depends(get_emission_calculation_service),
]
HotspotAnalysisService = Annotated[
    HotspotService,
    Depends(get_hotspot_service),
]
InterventionCatalogService = Annotated[
    InterventionService,
    Depends(get_intervention_service),
]
WhatIfSimulationService = Annotated[
    SimulationService,
    Depends(get_simulation_service),
]
ActionRoadmapService = Annotated[
    RoadmapService,
    Depends(get_roadmap_service),
]
FactoryDashboardService = Annotated[
    DashboardService,
    Depends(get_dashboard_service),
]
FactoryAnomalyService = Annotated[
    AnomalyService,
    Depends(get_anomaly_service),
]
CalculationReportService = Annotated[
    ReportService,
    Depends(get_report_service),
]
OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]


def _ensure_factory_access(
    session: Session,
    factory_id: int,
    user: User | None,
) -> Factory:
    factory = session.get(Factory, factory_id)
    if factory is None:
        raise HTTPException(status_code=404, detail="Factory not found")
    if factory.owner_id is not None and user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if factory.owner_id is not None and factory.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Factory access denied")
    return factory


def _calculation_for_user(
    session: Session,
    calculation_id: int,
    user: User | None,
) -> EmissionCalculation:
    calculation = session.scalar(
        select(EmissionCalculation)
        .options(selectinload(EmissionCalculation.reporting_period))
        .where(EmissionCalculation.id == calculation_id)
    )
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    _ensure_factory_access(session, calculation.reporting_period.factory_id, user)
    return calculation


@router.post(
    "/emission-factors",
    response_model=EmissionFactorRead,
    status_code=status.HTTP_201_CREATED,
)
def create_emission_factor(
    payload: EmissionFactorCreate,
    service: FactorService,
):
    return service.create_factor(**payload.model_dump())


@router.get("/emission-factors", response_model=list[EmissionFactorRead])
def list_emission_factors(service: FactorService):
    return service.list_factors()


@router.post(
    "/factories/{factory_id}/periods/{period_id}/calculate",
    response_model=EmissionCalculationRead,
)
def calculate_period(
    factory_id: int,
    period_id: int,
    service: CalculationService,
    user: OptionalUser,
):
    period = service.session.get(ReportingPeriod, period_id)
    if period is None or period.factory_id != factory_id:
        raise HTTPException(status_code=404, detail="Reporting period not found")
    _ensure_factory_access(service.session, factory_id, user)
    try:
        return service.calculate_period(period)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get(
    "/factories/{factory_id}/calculations",
    response_model=list[EmissionCalculationRead],
)
def list_calculations(
    factory_id: int,
    service: CalculationService,
    user: OptionalUser,
):
    _ensure_factory_access(service.session, factory_id, user)
    return service.list_calculations(factory_id)


@router.get(
    "/calculations/{calculation_id}/hotspots",
    response_model=list[HotspotRead],
)
def get_hotspots(
    calculation_id: int,
    service: HotspotAnalysisService,
    user: OptionalUser,
):
    _calculation_for_user(service.calculation_service.session, calculation_id, user)
    hotspots = service.get_hotspots(calculation_id)
    if hotspots is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return hotspots


@router.post(
    "/interventions",
    response_model=InterventionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_intervention(
    payload: InterventionCreate,
    service: InterventionCatalogService,
):
    return service.create_intervention(**payload.model_dump())


@router.get("/interventions", response_model=list[InterventionRead])
def list_interventions(service: InterventionCatalogService):
    return service.list_interventions()


@router.get(
    "/calculations/{calculation_id}/recommendations",
    response_model=list[RecommendationRead],
)
def get_recommendations(
    calculation_id: int,
    hotspot_service: HotspotAnalysisService,
    intervention_service: InterventionCatalogService,
    user: OptionalUser,
):
    _calculation_for_user(
        hotspot_service.calculation_service.session,
        calculation_id,
        user,
    )
    hotspots = hotspot_service.get_hotspots(calculation_id)
    if hotspots is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    ranked = intervention_service.rank_recommendations(hotspots)
    return [
        {
            "id": intervention.id,
            "name": intervention.name,
            "category": intervention.category,
            "target_source": intervention.target_source,
            "description": intervention.description,
            "estimated_cost": intervention.estimated_cost,
            "estimated_reduction_percentage": intervention.estimated_reduction_percentage,
            "feasibility": intervention.feasibility,
            "urgency": intervention.urgency,
            "recommendation_rank": rank,
            "hotspot_rank": hotspot.rank,
            "hotspot_source": hotspot.source,
            "hotspot_percentage": hotspot.percentage_of_total,
            "estimated_reduction_kg_co2e": reduction,
            "carbon_roi_kg_co2e_per_cost": carbon_roi,
            "priority_score": score,
            "rationale": rationale,
        }
        for rank, (
            intervention,
            hotspot,
            rationale,
            reduction,
            score,
            carbon_roi,
        ) in enumerate(
            ranked, 1
        )
    ]


@router.post(
    "/calculations/{calculation_id}/simulate",
    response_model=SimulationRead,
)
def simulate_calculation(
    calculation_id: int,
    payload: SimulationRequest,
    service: WhatIfSimulationService,
    user: OptionalUser,
):
    _calculation_for_user(
        service.calculation_service.session,
        calculation_id,
        user,
    )
    try:
        result = service.simulate(
            calculation_id,
            [item.model_dump() for item in payload.adjustments],
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return result


@router.get(
    "/calculations/{calculation_id}/roadmap",
    response_model=RoadmapRead,
)
def get_roadmap(
    calculation_id: int,
    service: ActionRoadmapService,
    user: OptionalUser,
):
    _calculation_for_user(
        service.hotspot_service.calculation_service.session,
        calculation_id,
        user,
    )
    roadmap = service.build(calculation_id)
    if roadmap is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return roadmap


@router.get(
    "/factories/{factory_id}/dashboard",
    response_model=DashboardRead,
)
def get_dashboard(
    factory_id: int,
    service: FactoryDashboardService,
    user: OptionalUser,
):
    _ensure_factory_access(
        service.calculation_service.session,
        factory_id,
        user,
    )
    return service.get_factory_dashboard(factory_id)


@router.get(
    "/factories/{factory_id}/anomalies",
    response_model=list[AnomalyRead],
)
def get_anomalies(
    factory_id: int,
    service: FactoryAnomalyService,
    user: OptionalUser,
):
    _ensure_factory_access(
        service.calculation_service.session,
        factory_id,
        user,
    )
    return service.detect_for_factory(factory_id)


@router.get(
    "/calculations/{calculation_id}/export.csv",
    response_class=Response,
    responses={200: {"content": {"text/csv": {}}}},
)
def export_calculation(
    calculation_id: int,
    service: CalculationReportService,
    user: OptionalUser,
):
    _calculation_for_user(
        service.calculation_service.session,
        calculation_id,
        user,
    )
    content = service.calculation_csv(calculation_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="ecotrace-calculation-{calculation_id}.csv"'
            )
        },
    )


@router.get(
    "/calculations/{calculation_id}",
    response_model=EmissionCalculationRead,
)
def get_calculation(calculation_id: int, service: CalculationService):
    calculation = service.get_calculation(calculation_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation
