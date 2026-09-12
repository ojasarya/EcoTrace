"""Application service for derived emission hotspots."""

from app.domain.hotspots import Hotspot, detect_hotspots
from app.services.emission_calculation_service import EmissionCalculationService


class HotspotService:
    """Derive ranked hotspots from persisted calculation breakdowns."""

    def __init__(self, calculation_service: EmissionCalculationService) -> None:
        self.calculation_service = calculation_service

    def get_hotspots(self, calculation_id: int) -> tuple[Hotspot, ...] | None:
        calculation = self.calculation_service.get_calculation(calculation_id)
        if calculation is None:
            return None
        return detect_hotspots(
            (
                (
                    item.category,
                    item.source,
                    item.kg_co2e,
                    item.percentage_of_total,
                )
                for item in calculation.breakdown
            )
        )
