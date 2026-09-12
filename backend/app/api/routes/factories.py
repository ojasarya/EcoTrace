"""Factory, reporting-period, and activity input endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_factory_service,
    get_current_user,
    get_optional_current_user,
    get_roadmap_action_service,
)
from app.db.models.activity import (
    EnergyUsage,
    MaterialUsage,
    ProductionActivity,
    TransportationActivity,
    WasteRecord,
)
from app.schemas.activity import (
    EnergyUsageCreate,
    EnergyUsageRead,
    MaterialUsageCreate,
    MaterialUsageRead,
    ProductionActivityCreate,
    ProductionActivityRead,
    TransportationActivityCreate,
    TransportationActivityRead,
    WasteRecordCreate,
    WasteRecordRead,
)
from app.schemas.factory import (
    FactoryCreate,
    FactoryRead,
    FactoryUpdate,
    ReportingPeriodCreate,
    ReportingPeriodRead,
)
from app.services.factory_service import FactoryService
from app.services.roadmap_action_service import RoadmapActionService
from app.db.models.user import User
from app.schemas.roadmap_action import (
    RoadmapActionCreate,
    RoadmapActionRead,
    RoadmapActionUpdate,
)

router = APIRouter(prefix="/factories", tags=["factories"])
Service = Annotated[FactoryService, Depends(get_factory_service)]
ActionService = Annotated[RoadmapActionService, Depends(get_roadmap_action_service)]


def _factory_or_404(service: FactoryService, factory_id: int):
    factory = service.get_factory(factory_id)
    if factory is None:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory


def _accessible_factory(
    service: FactoryService,
    factory_id: int,
    user: User | None,
):
    factory = _factory_or_404(service, factory_id)
    if factory.owner_id is not None and user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if factory.owner_id is not None and factory.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Factory access denied")
    return factory


def _period_or_404(
    service: FactoryService,
    factory_id: int,
    period_id: int,
    user: User | None,
):
    _accessible_factory(service, factory_id, user)
    period = service.get_period(factory_id, period_id)
    if period is None:
        raise HTTPException(status_code=404, detail="Reporting period not found")
    return period


OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]
CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post("", response_model=FactoryRead, status_code=status.HTTP_201_CREATED)
def create_factory(
    payload: FactoryCreate,
    service: Service,
    user: OptionalUser,
):
    values = payload.model_dump()
    if user is not None:
        values["owner_id"] = user.id
    return service.create_factory(**values)


@router.get("", response_model=list[FactoryRead])
def list_factories(service: Service, user: OptionalUser):
    return service.list_accessible_factories(user.id if user is not None else None)


@router.get("/mine", response_model=list[FactoryRead])
def list_my_factories(service: Service, user: CurrentUser):
    return service.list_factories_for_owner(user.id)


@router.get("/{factory_id}", response_model=FactoryRead)
def get_factory(factory_id: int, service: Service, user: OptionalUser):
    return _accessible_factory(service, factory_id, user)


@router.patch("/{factory_id}", response_model=FactoryRead)
def update_factory(
    factory_id: int,
    payload: FactoryUpdate,
    service: Service,
    user: OptionalUser,
):
    factory = _accessible_factory(service, factory_id, user)
    return service.update_factory(
        factory,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factory(factory_id: int, service: Service, user: OptionalUser):
    service.delete_factory(_accessible_factory(service, factory_id, user))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{factory_id}/roadmap-actions",
    response_model=RoadmapActionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_roadmap_action(
    factory_id: int,
    payload: RoadmapActionCreate,
    service: ActionService,
    factory_service: Service,
    user: OptionalUser,
):
    _accessible_factory(factory_service, factory_id, user)
    try:
        return service.create_action(factory_id, **payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get(
    "/{factory_id}/roadmap-actions",
    response_model=list[RoadmapActionRead],
)
def list_roadmap_actions(
    factory_id: int,
    service: ActionService,
    factory_service: Service,
    user: OptionalUser,
):
    _accessible_factory(factory_service, factory_id, user)
    return service.list_actions(factory_id)


@router.patch(
    "/{factory_id}/roadmap-actions/{action_id}",
    response_model=RoadmapActionRead,
)
def update_roadmap_action(
    factory_id: int,
    action_id: int,
    payload: RoadmapActionUpdate,
    service: ActionService,
    factory_service: Service,
    user: OptionalUser,
):
    _accessible_factory(factory_service, factory_id, user)
    action = service.get_action(factory_id, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Roadmap action not found")
    return service.update_action(action, **payload.model_dump(exclude_unset=True))


@router.post(
    "/{factory_id}/periods",
    response_model=ReportingPeriodRead,
    status_code=status.HTTP_201_CREATED,
)
def create_period(
    factory_id: int,
    payload: ReportingPeriodCreate,
    service: Service,
    user: OptionalUser,
):
    factory = _accessible_factory(service, factory_id, user)
    return service.create_period(factory, **payload.model_dump())


@router.get("/{factory_id}/periods", response_model=list[ReportingPeriodRead])
def list_periods(factory_id: int, service: Service, user: OptionalUser):
    _accessible_factory(service, factory_id, user)
    return service.list_periods(factory_id)


@router.post(
    "/{factory_id}/periods/{period_id}/production",
    response_model=ProductionActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_production_activity(
    factory_id: int,
    period_id: int,
    payload: ProductionActivityCreate,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.create_activity(
        period,
        ProductionActivity,
        **payload.model_dump(),
    )


@router.get(
    "/{factory_id}/periods/{period_id}/production",
    response_model=list[ProductionActivityRead],
)
def list_production_activity(
    factory_id: int,
    period_id: int,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.list_activities(period, ProductionActivity)


@router.post(
    "/{factory_id}/periods/{period_id}/energy",
    response_model=EnergyUsageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_energy_usage(
    factory_id: int,
    period_id: int,
    payload: EnergyUsageCreate,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.create_activity(period, EnergyUsage, **payload.model_dump())


@router.get(
    "/{factory_id}/periods/{period_id}/energy",
    response_model=list[EnergyUsageRead],
)
def list_energy_usage(
    factory_id: int,
    period_id: int,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.list_activities(period, EnergyUsage)


@router.post(
    "/{factory_id}/periods/{period_id}/materials",
    response_model=MaterialUsageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_material_usage(
    factory_id: int,
    period_id: int,
    payload: MaterialUsageCreate,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.create_activity(period, MaterialUsage, **payload.model_dump())


@router.get(
    "/{factory_id}/periods/{period_id}/materials",
    response_model=list[MaterialUsageRead],
)
def list_material_usage(
    factory_id: int,
    period_id: int,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.list_activities(period, MaterialUsage)


@router.post(
    "/{factory_id}/periods/{period_id}/waste",
    response_model=WasteRecordRead,
    status_code=status.HTTP_201_CREATED,
)
def create_waste_record(
    factory_id: int,
    period_id: int,
    payload: WasteRecordCreate,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.create_activity(period, WasteRecord, **payload.model_dump())


@router.get(
    "/{factory_id}/periods/{period_id}/waste",
    response_model=list[WasteRecordRead],
)
def list_waste_records(
    factory_id: int,
    period_id: int,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.list_activities(period, WasteRecord)


@router.post(
    "/{factory_id}/periods/{period_id}/transportation",
    response_model=TransportationActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transportation_activity(
    factory_id: int,
    period_id: int,
    payload: TransportationActivityCreate,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.create_activity(
        period,
        TransportationActivity,
        **payload.model_dump(),
    )


@router.get(
    "/{factory_id}/periods/{period_id}/transportation",
    response_model=list[TransportationActivityRead],
)
def list_transportation_activity(
    factory_id: int,
    period_id: int,
    service: Service,
    user: OptionalUser,
):
    period = _period_or_404(service, factory_id, period_id, user)
    return service.list_activities(period, TransportationActivity)
