"""Repeatable demo dataset creation for local development."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.activity import EnergyUsage, MaterialUsage, WasteRecord
from app.db.models.emission_factor import EmissionFactor
from app.db.models.factory import Factory, ReportingPeriod
from app.db.models.intervention import Intervention
from app.services.emission_calculation_service import EmissionCalculationService


DEMO_FACTORY_NAME = "EcoTrace Demo Factory"


def seed_demo_data(session: Session) -> Factory:
    """Create the complete demo dataset once and calculate its emissions."""

    existing = session.scalar(
        select(Factory).where(Factory.name == DEMO_FACTORY_NAME)
    )
    if existing is not None:
        return existing

    factory = Factory(
        name=DEMO_FACTORY_NAME,
        industry_type="Manufacturing",
        location="Ahmedabad",
        production_unit="tonnes",
    )
    period = ReportingPeriod(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 1, 31),
        production_quantity=Decimal("1000"),
        production_unit="tonnes",
    )
    period.energy_usage.append(
        EnergyUsage(
            source="grid electricity",
            quantity=Decimal("10000"),
            unit="kwh",
            renewable_percentage=Decimal("0"),
        )
    )
    period.material_usage.append(
        MaterialUsage(
            material_name="steel",
            material_type="metal",
            quantity=Decimal("2000"),
            unit="kg",
            recycled_content_percentage=Decimal("10"),
        )
    )
    period.waste_records.append(
        WasteRecord(
            waste_type="industrial waste",
            quantity=Decimal("100"),
            unit="kg",
            disposal_method="landfill",
            recycled_quantity=Decimal("0"),
        )
    )
    factory.reporting_periods.append(period)
    session.add(factory)
    session.flush()

    session.add_all(
        [
            EmissionFactor(
                category="energy",
                source="grid electricity",
                unit="kwh",
                kg_co2e_per_unit=Decimal("0.4"),
                geography="India",
                source_reference="EcoTrace demo factor",
                valid_from=date(2026, 1, 1),
                version="demo-1",
            ),
            EmissionFactor(
                category="materials",
                source="steel",
                unit="kg",
                kg_co2e_per_unit=Decimal("2"),
                geography="Global",
                source_reference="EcoTrace demo factor",
                valid_from=date(2026, 1, 1),
                version="demo-1",
            ),
            EmissionFactor(
                category="waste",
                source="industrial waste",
                unit="kg",
                kg_co2e_per_unit=Decimal("1.5"),
                geography="Global",
                source_reference="EcoTrace demo factor",
                valid_from=date(2026, 1, 1),
                version="demo-1",
            ),
        ]
    )
    session.add_all(
        [
            Intervention(
                name="Renewable electricity",
                category="energy",
                target_source="grid electricity",
                description="Source a renewable electricity mix for grid consumption.",
                estimated_cost=Decimal("25000"),
                estimated_reduction_percentage=Decimal("45"),
                feasibility="medium",
                urgency="high",
            ),
            Intervention(
                name="Steel scrap substitution",
                category="materials",
                target_source="steel",
                description="Increase recycled steel content in production inputs.",
                estimated_cost=Decimal("18000"),
                estimated_reduction_percentage=Decimal("25"),
                feasibility="high",
                urgency="medium",
            ),
            Intervention(
                name="Waste recovery",
                category="waste",
                target_source="industrial waste",
                description="Divert industrial waste from landfill to recovery partners.",
                estimated_cost=Decimal("7000"),
                estimated_reduction_percentage=Decimal("60"),
                feasibility="high",
                urgency="high",
            ),
        ]
    )
    session.flush()
    EmissionCalculationService(session).calculate_period(period)
    return factory
