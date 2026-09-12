"""Emission factor and calculation endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_emission_calculation_service,
    get_emission_factor_service,
    get_hotspot_service,
    get_intervention_service,
)
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
from app.services.emission_calculation_service import EmissionCalculationService
from app.services.emission_factor_service import EmissionFactorService
from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService

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
):
    period = service.session.get(ReportingPeriod, period_id)
    if period is None or period.factory_id != factory_id:
        raise HTTPException(status_code=404, detail="Reporting period not found")
    try:
        return service.calculate_period(period)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get(
    "/factories/{factory_id}/calculations",
    response_model=list[EmissionCalculationRead],
)
def list_calculations(factory_id: int, service: CalculationService):
    return service.list_calculations(factory_id)


@router.get(
    "/calculations/{calculation_id}/hotspots",
    response_model=list[HotspotRead],
)
def get_hotspots(calculation_id: int, service: HotspotAnalysisService):
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
):
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


@router.get(
    "/calculations/{calculation_id}",
    response_model=EmissionCalculationRead,
)
def get_calculation(calculation_id: int, service: CalculationService):
    calculation = service.get_calculation(calculation_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation
