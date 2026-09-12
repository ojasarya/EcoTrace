"""Application service for non-persisted what-if simulations."""

from decimal import Decimal

from app.domain.simulations import simulate_emissions
from app.services.emission_calculation_service import EmissionCalculationService


class SimulationService:
    """Simulate source reductions against an existing calculation."""

    def __init__(self, calculation_service: EmissionCalculationService) -> None:
        self.calculation_service = calculation_service

    def simulate(self, calculation_id: int, adjustments: list[dict[str, object]]):
        calculation = self.calculation_service.get_calculation(calculation_id)
        if calculation is None:
            return None
        reductions = {
            (str(item["category"]).casefold(), str(item["source"]).casefold()): Decimal(
                str(item["reduction_percentage"])
            )
            for item in adjustments
        }
        baseline, simulated, breakdown = simulate_emissions(
            (
                (item.category, item.source, item.kg_co2e)
                for item in calculation.breakdown
            ),
            reductions,
        )
        reduction = baseline - simulated
        percentage = reduction * Decimal("100") / baseline if baseline else Decimal("0")
        return {
            "calculation_id": calculation_id,
            "baseline_kg_co2e": baseline,
            "simulated_kg_co2e": simulated,
            "reduction_kg_co2e": reduction,
            "reduction_percentage": percentage,
            "breakdown": [
                {
                    "category": category,
                    "source": source,
                    "simulated_kg_co2e": amount,
                }
                for category, source, amount in breakdown
            ],
        }
