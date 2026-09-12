from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import (
    EmissionBreakdown,
    EmissionCalculation,
    EmissionFactor,
    EnergyUsage,
    Factory,
    MaterialUsage,
    ReportingPeriod,
)


def test_model_metadata_contains_initial_schema() -> None:
    expected_tables = {
        "factories",
        "reporting_periods",
        "production_activities",
        "energy_usage",
        "material_usage",
        "waste_records",
        "transportation_activities",
        "emission_factors",
        "emission_calculations",
        "emission_breakdowns",
    }

    assert expected_tables == set(Base.metadata.tables)


def test_models_persist_factory_activity_and_calculation_relationships() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        factory = Factory(
            name="Demo Factory",
            industry_type="Manufacturing",
            location="Ahmedabad",
            production_unit="units",
        )
        period = ReportingPeriod(
            period_start=date(2026, 9, 1),
            period_end=date(2026, 9, 30),
            production_quantity=24000,
            production_unit="units",
        )
        period.energy_usage.append(
            EnergyUsage(
                source="grid electricity",
                quantity=Decimal("24000"),
                unit="kWh",
            )
        )
        period.material_usage.append(
            MaterialUsage(
                material_name="steel",
                material_type="primary",
                quantity=Decimal("12000"),
                unit="kg",
            )
        )
        factory.reporting_periods.append(period)
        calculation = EmissionCalculation(
            total_kg_co2e=Decimal("10000"),
            calculation_version="1.0",
        )
        calculation.breakdown.append(
            EmissionBreakdown(
                category="energy",
                source="grid electricity",
                activity_quantity=Decimal("24000"),
                activity_unit="kWh",
                applied_factor=Decimal("0.4"),
                kg_co2e=Decimal("9600"),
                percentage_of_total=Decimal("96"),
            )
        )
        period.calculations.append(calculation)
        session.add(factory)
        session.commit()

        loaded = session.get(Factory, factory.id)
        assert loaded is not None
        assert loaded.reporting_periods[0].energy_usage[0].source == "grid electricity"
        assert loaded.reporting_periods[0].calculations[0].breakdown[0].kg_co2e == Decimal("9600.000000")


def test_migration_schema_matches_model_table_names() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == set(Base.metadata.tables)
