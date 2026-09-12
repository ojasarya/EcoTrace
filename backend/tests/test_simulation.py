from decimal import Decimal

import pytest

from app.domain.simulations import simulate_emissions


def test_simulation_reduces_only_selected_source() -> None:
    baseline, total, breakdown = simulate_emissions(
        [("energy", "grid", Decimal("70")), ("waste", "landfill", Decimal("30"))],
        {("energy", "GRID"): Decimal("50")},
    )
    assert baseline == Decimal("100")
    assert total == Decimal("65")
    assert breakdown[0][2] == Decimal("35")
    assert breakdown[1][2] == Decimal("30")


def test_simulation_rejects_invalid_reduction() -> None:
    with pytest.raises(ValueError):
        simulate_emissions(
            [("energy", "grid", Decimal("70"))],
            {("energy", "grid"): Decimal("101")},
        )
