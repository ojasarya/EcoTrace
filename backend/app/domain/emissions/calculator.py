"""Deterministic emission calculation rules."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Sequence


def _decimal(value: Decimal | int | float, field_name: str) -> Decimal:
    try:
        converted = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a valid number") from None

    if not converted.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return converted


def _identifier(value: str, field_name: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


@dataclass(frozen=True)
class EmissionActivity:
    """A measurable activity that produces emissions."""

    category: str
    source: str
    quantity: Decimal | int | float
    unit: str


@dataclass(frozen=True)
class EmissionFactor:
    """A factor expressed as kg CO2e per unit of activity."""

    category: str
    source: str
    unit: str
    kg_co2e_per_unit: Decimal | int | float


@dataclass(frozen=True)
class EmissionBreakdown:
    """The calculated emissions for one activity."""

    category: str
    source: str
    quantity: Decimal
    unit: str
    kg_co2e: Decimal
    percentage_of_total: Decimal


@dataclass(frozen=True)
class EmissionCalculation:
    """The complete result of an emission calculation."""

    total_kg_co2e: Decimal
    breakdown: tuple[EmissionBreakdown, ...]
    category_totals_kg_co2e: dict[str, Decimal]
    source_totals_kg_co2e: dict[str, Decimal]


def calculate_emissions(
    activities: Sequence[EmissionActivity],
    factors: Sequence[EmissionFactor],
) -> EmissionCalculation:
    """Calculate total and categorized emissions for the supplied activities."""

    factor_map: dict[tuple[str, str, str], Decimal] = {}
    for factor in factors:
        key = (
            _identifier(factor.category, "factor category"),
            _identifier(factor.source, "factor source"),
            _identifier(factor.unit, "factor unit"),
        )
        if key in factor_map:
            raise ValueError(
                f"duplicate emission factor for "
                f"{key[0]}/{key[1]}/{key[2]}"
            )

        factor_value = _decimal(factor.kg_co2e_per_unit, "emission factor")
        if factor_value < 0:
            raise ValueError("emission factor must not be negative")
        factor_map[key] = factor_value

    calculated: list[tuple[str, str, Decimal, str, Decimal]] = []
    category_totals: dict[str, Decimal] = {}
    source_totals: dict[str, Decimal] = {}

    for activity in activities:
        category = _identifier(activity.category, "activity category")
        source = _identifier(activity.source, "activity source")
        unit = _identifier(activity.unit, "activity unit")
        quantity = _decimal(activity.quantity, "activity quantity")
        if quantity < 0:
            raise ValueError("activity quantity must not be negative")

        factor = factor_map.get((category, source, unit))
        if factor is None:
            raise ValueError(
                f"no emission factor found for {category}/{source}/{unit}"
            )

        kg_co2e = quantity * factor
        calculated.append((category, source, quantity, unit, kg_co2e))
        category_totals[category] = category_totals.get(category, Decimal("0")) + kg_co2e
        source_totals[source] = source_totals.get(source, Decimal("0")) + kg_co2e

    total = sum((entry[4] for entry in calculated), Decimal("0"))
    breakdown = tuple(
        EmissionBreakdown(
            category=category,
            source=source,
            quantity=quantity,
            unit=unit,
            kg_co2e=kg_co2e,
            percentage_of_total=(
                (kg_co2e / total * Decimal("100")) if total else Decimal("0")
            ),
        )
        for category, source, quantity, unit, kg_co2e in calculated
    )

    return EmissionCalculation(
        total_kg_co2e=total,
        breakdown=breakdown,
        category_totals_kg_co2e=category_totals,
        source_totals_kg_co2e=source_totals,
    )
