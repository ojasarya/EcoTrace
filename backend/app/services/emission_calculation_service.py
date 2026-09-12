"""Application service for database-backed emission calculations."""

from collections.abc import Iterable
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.activity import (
    EnergyUsage,
    MaterialUsage,
    ProductionActivity,
    TransportationActivity,
    WasteRecord,
)
from app.db.models.calculation import EmissionBreakdown, EmissionCalculation
from app.db.models.emission_factor import EmissionFactor
from app.db.models.factory import ReportingPeriod
from app.domain.emissions.calculator import (
    EmissionActivity,
    EmissionFactor as DomainEmissionFactor,
    calculate_emissions,
)


class EmissionCalculationService:
    """Load activity data, calculate emissions, and persist the result."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def calculate_period(
        self,
        period: ReportingPeriod,
        calculation_version: str = "1.0",
    ) -> EmissionCalculation:
        activities = list(self._activities_for(period))
        factors = list(
            self.session.scalars(
                select(EmissionFactor).order_by(EmissionFactor.id)
            )
        )
        result = calculate_emissions(activities, [
            DomainEmissionFactor(
                category=factor.category,
                source=factor.source,
                unit=factor.unit,
                kg_co2e_per_unit=factor.kg_co2e_per_unit,
            )
            for factor in factors
        ])

        calculation = EmissionCalculation(
            reporting_period=period,
            total_kg_co2e=result.total_kg_co2e,
            calculation_version=calculation_version,
            status="completed",
        )
        calculation.breakdown = [
            EmissionBreakdown(
                category=item.category,
                source=item.source,
                activity_quantity=item.quantity,
                activity_unit=item.unit,
                applied_factor=self._factor_for(
                    factors, item.category, item.source, item.unit
                ),
                kg_co2e=item.kg_co2e,
                percentage_of_total=item.percentage_of_total,
            )
            for item in result.breakdown
        ]
        self.session.add(calculation)
        self.session.commit()
        self.session.refresh(calculation)
        return calculation

    def get_calculation(self, calculation_id: int) -> EmissionCalculation | None:
        return self.session.scalar(
            select(EmissionCalculation)
            .options(selectinload(EmissionCalculation.breakdown))
            .where(EmissionCalculation.id == calculation_id)
        )

    def list_calculations(self, factory_id: int) -> list[EmissionCalculation]:
        return list(
            self.session.scalars(
                select(EmissionCalculation)
                .join(ReportingPeriod)
                .options(selectinload(EmissionCalculation.breakdown))
                .where(ReportingPeriod.factory_id == factory_id)
                .order_by(EmissionCalculation.id.desc())
            )
        )

    def _activities_for(
        self,
        period: ReportingPeriod,
    ) -> Iterable[EmissionActivity]:
        for item in period.energy_usage:
            yield EmissionActivity("energy", item.source, item.quantity, item.unit)
        for item in period.material_usage:
            yield EmissionActivity("materials", item.material_name, item.quantity, item.unit)
        for item in period.waste_records:
            yield EmissionActivity("waste", item.waste_type, item.quantity, item.unit)
        for item in period.transportation_activities:
            yield EmissionActivity(
                "transportation",
                item.mode,
                item.distance * item.load_quantity,
                f"{item.distance_unit}-{item.load_unit}",
            )
        for item in period.production_activities:
            yield EmissionActivity("processes", item.process_name, item.quantity, item.unit)

    @staticmethod
    def _factor_for(
        factors: list[EmissionFactor],
        category: str,
        source: str,
        unit: str,
    ) -> Decimal:
        for factor in factors:
            if (
                factor.category.strip().lower() == category
                and factor.source.strip().lower() == source
                and factor.unit.strip().lower() == unit
            ):
                return Decimal(str(factor.kg_co2e_per_unit))
        raise ValueError(f"no emission factor found for {category}/{source}/{unit}")
