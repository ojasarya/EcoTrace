"""Persistence services for factories, periods, and activity inputs."""

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.activity import (
    EnergyUsage,
    MaterialUsage,
    ProductionActivity,
    TransportationActivity,
    WasteRecord,
)
from app.db.models.factory import Factory, ReportingPeriod

ModelT = TypeVar("ModelT")


class FactoryService:
    """Encapsulate database operations used by factory activity routes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_factory(self, **values: object) -> Factory:
        factory = Factory(**values)
        self.session.add(factory)
        self.session.commit()
        self.session.refresh(factory)
        return factory

    def list_factories(self) -> list[Factory]:
        return list(self.session.scalars(select(Factory).order_by(Factory.id)))

    def list_factories_for_owner(self, owner_id: int) -> list[Factory]:
        return list(
            self.session.scalars(
                select(Factory)
                .where(Factory.owner_id == owner_id)
                .order_by(Factory.id)
            )
        )

    def get_factory(self, factory_id: int) -> Factory | None:
        return self.session.get(Factory, factory_id)

    def update_factory(self, factory: Factory, **values: object) -> Factory:
        for key, value in values.items():
            setattr(factory, key, value)
        self.session.commit()
        self.session.refresh(factory)
        return factory

    def delete_factory(self, factory: Factory) -> None:
        self.session.delete(factory)
        self.session.commit()

    def create_period(self, factory: Factory, **values: object) -> ReportingPeriod:
        period = ReportingPeriod(factory=factory, **values)
        self.session.add(period)
        self.session.commit()
        self.session.refresh(period)
        return period

    def get_period(self, factory_id: int, period_id: int) -> ReportingPeriod | None:
        return self.session.scalar(
            select(ReportingPeriod).where(
                ReportingPeriod.id == period_id,
                ReportingPeriod.factory_id == factory_id,
            )
        )

    def list_periods(self, factory_id: int) -> list[ReportingPeriod]:
        return list(
            self.session.scalars(
                select(ReportingPeriod)
                .where(ReportingPeriod.factory_id == factory_id)
                .order_by(ReportingPeriod.period_start.desc())
            )
        )

    def create_activity(
        self,
        period: ReportingPeriod,
        model: type[ModelT],
        **values: object,
    ) -> ModelT:
        activity = model(reporting_period=period, **values)
        self.session.add(activity)
        self.session.commit()
        self.session.refresh(activity)
        return activity

    def list_activities(
        self,
        period: ReportingPeriod,
        model: type[ModelT],
    ) -> list[ModelT]:
        return list(
            self.session.scalars(
                select(model).where(
                    model.reporting_period_id == period.id,
                )
            )
        )


ACTIVITY_MODELS: dict[str, type] = {
    "production": ProductionActivity,
    "energy": EnergyUsage,
    "materials": MaterialUsage,
    "waste": WasteRecord,
    "transportation": TransportationActivity,
}
