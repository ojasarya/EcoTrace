"""Application service for calculating factory emissions."""

from collections.abc import Sequence

from app.domain.emissions.calculator import (
    EmissionActivity,
    EmissionCalculation,
    EmissionFactor,
    calculate_emissions,
)


class EmissionService:
    """Coordinate emission calculations independently of transport or persistence."""

    def calculate(
        self,
        activities: Sequence[EmissionActivity],
        factors: Sequence[EmissionFactor],
    ) -> EmissionCalculation:
        """Calculate emissions using the supplied activities and factor snapshot."""

        return calculate_emissions(activities, factors)
