from decimal import Decimal

import pytest

from app.domain.emissions.calculator import EmissionActivity, EmissionFactor
from app.services.emission_service import EmissionService


service = EmissionService()


def test_calculate_returns_total_and_category_breakdown() -> None:
    result = service.calculate(
        activities=[
            EmissionActivity("Energy", "Grid electricity", 100, "kWh"),
            EmissionActivity("Waste", "Landfill", 2, "tonne"),
        ],
        factors=[
            EmissionFactor("energy", "grid electricity", "kWh", 0.4),
            EmissionFactor("waste", "landfill", "tonne", 500),
        ],
    )

    assert result.total_kg_co2e == Decimal("1040.0")
    assert result.category_totals_kg_co2e == {
        "energy": Decimal("40.0"),
        "waste": Decimal("1000"),
    }
    assert result.source_totals_kg_co2e["grid electricity"] == Decimal("40.0")
    assert result.breakdown[0].percentage_of_total == Decimal("40.0") * Decimal("100") / Decimal("1040")
    assert result.breakdown[1].percentage_of_total == Decimal("1000") * Decimal("100") / Decimal("1040")


def test_calculate_accepts_case_and_whitespace_variations() -> None:
    result = service.calculate(
        [EmissionActivity(" Electricity ", " Grid ", 10, " KWH ")],
        [EmissionFactor("electricity", "grid", "kwh", 0.5)],
    )

    assert result.total_kg_co2e == Decimal("5.0")
    assert result.breakdown[0].category == "electricity"


@pytest.mark.parametrize(
    ("activities", "factors", "message"),
    [
        (
            [EmissionActivity("energy", "grid", -1, "kWh")],
            [EmissionFactor("energy", "grid", "kWh", 0.4)],
            "activity quantity must not be negative",
        ),
        (
            [EmissionActivity("energy", "grid", 1, "kWh")],
            [],
            "no emission factor found",
        ),
        (
            [EmissionActivity("energy", "grid", 1, "kWh")],
            [
                EmissionFactor("energy", "grid", "kWh", 0.4),
                EmissionFactor("energy", "grid", "kWh", 0.5),
            ],
            "duplicate emission factor",
        ),
    ],
)
def test_calculate_rejects_invalid_inputs(
    activities: list[EmissionActivity],
    factors: list[EmissionFactor],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        service.calculate(activities, factors)


def test_zero_emissions_have_zero_percentages() -> None:
    result = service.calculate(
        [EmissionActivity("energy", "renewable electricity", 100, "kWh")],
        [EmissionFactor("energy", "renewable electricity", "kWh", 0)],
    )

    assert result.total_kg_co2e == Decimal("0")
    assert result.breakdown[0].percentage_of_total == Decimal("0")
