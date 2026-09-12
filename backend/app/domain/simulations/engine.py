"""Deterministic scenario simulation over persisted emission breakdowns."""

from decimal import Decimal
from typing import Iterable


def simulate_emissions(
    breakdown: Iterable[tuple[str, str, Decimal]],
    reductions: dict[tuple[str, str], Decimal],
) -> tuple[Decimal, Decimal, tuple[tuple[str, str, Decimal], ...]]:
    """Apply source-level percentage reductions without changing stored data."""

    simulated: list[tuple[str, str, Decimal]] = []
    baseline = Decimal("0")
    total = Decimal("0")
    normalized_reductions = {
        (key[0].casefold(), key[1].casefold()): value
        for key, value in reductions.items()
    }
    for category, source, amount in breakdown:
        baseline += amount
        reduction = normalized_reductions.get(
            (category.casefold(), source.casefold()), Decimal("0")
        )
        if reduction < 0 or reduction > 100:
            raise ValueError("Reduction percentage must be between 0 and 100")
        simulated_amount = amount * (Decimal("100") - reduction) / Decimal("100")
        total += simulated_amount
        simulated.append((category, source, simulated_amount))
    return baseline, total, tuple(simulated)
