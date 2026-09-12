"""Application service for historical emissions anomaly detection."""

from app.domain.anomalies import detect_anomalies
from app.services.emission_calculation_service import EmissionCalculationService


class AnomalyService:
    """Analyze a factory's persisted calculation history."""

    def __init__(self, calculation_service: EmissionCalculationService) -> None:
        self.calculation_service = calculation_service

    def detect_for_factory(self, factory_id: int) -> list[dict[str, object]]:
        calculations = self.calculation_service.list_calculations(factory_id)
        results = detect_anomalies(
            [(calculation.id, calculation.total_kg_co2e) for calculation in calculations]
        )
        by_id = {calculation.id: calculation for calculation in calculations}
        return [
            {
                "calculation_id": calculation_id,
                "total_kg_co2e": by_id[calculation_id].total_kg_co2e,
                "is_anomaly": is_anomaly,
                "anomaly_score": score,
                "explanation": (
                    "This calculation is an unusual emissions pattern compared "
                    "with the factory history."
                    if is_anomaly
                    else "This calculation is consistent with the factory history."
                ),
            }
            for calculation_id, is_anomaly, score in results
        ]
