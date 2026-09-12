"""Deterministic carbon return calculations."""

from decimal import Decimal


def calculate_carbon_roi(
    reduction_kg_co2e: Decimal, implementation_cost: Decimal
) -> Decimal | None:
    """Return expected kg CO2e reduction per cost unit."""

    if reduction_kg_co2e < 0:
        raise ValueError("Reduction cannot be negative")
    if implementation_cost < 0:
        raise ValueError("Implementation cost cannot be negative")
    if implementation_cost == 0:
        return None
    return reduction_kg_co2e / implementation_cost
