"""Application service for derived prioritized action roadmaps."""

from decimal import Decimal

from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService


class RoadmapService:
    """Build an ordered roadmap without mutating calculation data."""

    def __init__(
        self,
        hotspot_service: HotspotService,
        intervention_service: InterventionService,
    ) -> None:
        self.hotspot_service = hotspot_service
        self.intervention_service = intervention_service

    def build(self, calculation_id: int):
        hotspots = self.hotspot_service.get_hotspots(calculation_id)
        if hotspots is None:
            return None
        recommendations = self.intervention_service.rank_recommendations(hotspots)
        cumulative_cost = Decimal("0")
        cumulative_reduction = Decimal("0")
        actions = []
        for sequence, (
            intervention,
            hotspot,
            rationale,
            reduction,
            _score,
            _roi,
        ) in enumerate(recommendations, 1):
            cumulative_cost += intervention.estimated_cost
            cumulative_reduction += reduction
            phase = "immediate" if sequence <= 2 else "planned"
            actions.append(
                {
                    "sequence": sequence,
                    "recommendation_rank": sequence,
                    "intervention_id": intervention.id,
                    "intervention_name": intervention.name,
                    "target_source": hotspot.source,
                    "phase": phase,
                    "estimated_cost": intervention.estimated_cost,
                    "estimated_reduction_kg_co2e": reduction,
                    "cumulative_cost": cumulative_cost,
                    "cumulative_reduction_kg_co2e": cumulative_reduction,
                    "rationale": rationale,
                }
            )
        return {
            "calculation_id": calculation_id,
            "total_actions": len(actions),
            "total_estimated_cost": cumulative_cost,
            "total_estimated_reduction_kg_co2e": cumulative_reduction,
            "actions": actions,
        }
