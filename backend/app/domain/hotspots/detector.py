"""Deterministic emission hotspot detection and explanations."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class Hotspot:
    """A ranked emission source with an explainable severity."""

    category: str
    source: str
    kg_co2e: Decimal
    percentage_of_total: Decimal
    severity: str
    rank: int
    explanation: str


def _severity(percentage: Decimal) -> str:
    if percentage > Decimal("30"):
        return "high"
    if percentage >= Decimal("15"):
        return "moderate"
    return "low"


def detect_hotspots(
    breakdown: Iterable[tuple[str, str, Decimal, Decimal]],
) -> tuple[Hotspot, ...]:
    """Rank breakdown rows and explain their relative contribution."""

    rows = sorted(breakdown, key=lambda row: row[2], reverse=True)
    return tuple(
        Hotspot(
            category=category,
            source=source,
            kg_co2e=kg_co2e,
            percentage_of_total=percentage,
            severity=_severity(percentage),
            rank=index,
            explanation=(
                f"{source} is ranked hotspot {index}, contributing "
                f"{percentage.normalize()}% of total emissions "
                f"({kg_co2e.normalize()} kg CO2e)."
            ),
        )
        for index, (category, source, kg_co2e, percentage) in enumerate(rows, 1)
    )
