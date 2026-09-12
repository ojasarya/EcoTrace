from decimal import Decimal

import pytest

from app.domain.recommendations import calculate_carbon_roi


def test_carbon_roi_is_reduction_per_cost() -> None:
    assert calculate_carbon_roi(Decimal("40"), Decimal("5000")) == Decimal("0.008")


def test_zero_cost_has_no_finite_roi() -> None:
    assert calculate_carbon_roi(Decimal("40"), Decimal("0")) is None


@pytest.mark.parametrize(
    "reduction,cost",
    [(Decimal("-1"), Decimal("10")), (Decimal("1"), Decimal("-10"))],
)
def test_carbon_roi_rejects_negative_values(
    reduction: Decimal, cost: Decimal
) -> None:
    with pytest.raises(ValueError):
        calculate_carbon_roi(reduction, cost)
