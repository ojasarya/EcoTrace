"""Read-only factory dashboard aggregation service."""

from collections import defaultdict
from decimal import Decimal

from app.services.emission_calculation_service import EmissionCalculationService
from app.services.hotspot_service import HotspotService
from app.services.intervention_service import InterventionService
from app.services.roadmap_service import RoadmapService


class DashboardService:
    """Compose persisted calculations and derived analysis for a factory."""

    def __init__(
        self,
        calculation_service: EmissionCalculationService,
        hotspot_service: HotspotService,
        intervention_service: InterventionService,
        roadmap_service: RoadmapService,
    ) -> None:
        self.calculation_service = calculation_service
        self.hotspot_service = hotspot_service
        self.intervention_service = intervention_service
        self.roadmap_service = roadmap_service

    def get_factory_dashboard(self, factory_id: int):
        calculations = self.calculation_service.list_calculations(factory_id)
        if not calculations:
            return {
                "factory_id": factory_id,
                "calculation_id": None,
                "total_kg_co2e": Decimal("0"),
                "categories": [],
                "hotspots": [],
                "recommendations": [],
                "roadmap": [],
            }
        calculation = calculations[0]
        hotspots = self.hotspot_service.get_hotspots(calculation.id) or ()
        ranked = self.intervention_service.rank_recommendations(hotspots)
        recommendations = [
            {
                "id": intervention.id,
                "name": intervention.name,
                "category": intervention.category,
                "target_source": intervention.target_source,
                "description": intervention.description,
                "estimated_cost": intervention.estimated_cost,
                "estimated_reduction_percentage": intervention.estimated_reduction_percentage,
                "feasibility": intervention.feasibility,
                "urgency": intervention.urgency,
                "recommendation_rank": rank,
                "hotspot_rank": hotspot.rank,
                "hotspot_source": hotspot.source,
                "hotspot_percentage": hotspot.percentage_of_total,
                "estimated_reduction_kg_co2e": reduction,
                "carbon_roi_kg_co2e_per_cost": roi,
                "priority_score": score,
                "rationale": rationale,
            }
            for rank, (
                intervention,
                hotspot,
                rationale,
                reduction,
                score,
                roi,
            ) in enumerate(ranked, 1)
        ]
        roadmap = self.roadmap_service.build(calculation.id)
        category_totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for item in calculation.breakdown:
            category_totals[item.category] += item.kg_co2e
        categories = [
            {
                "category": category,
                "kg_co2e": amount,
                "percentage_of_total": (
                    amount * Decimal("100") / calculation.total_kg_co2e
                    if calculation.total_kg_co2e
                    else Decimal("0")
                ),
            }
            for category, amount in sorted(category_totals.items())
        ]
        return {
            "factory_id": factory_id,
            "calculation_id": calculation.id,
            "total_kg_co2e": calculation.total_kg_co2e,
            "categories": categories,
            "hotspots": list(hotspots),
            "recommendations": recommendations,
            "roadmap": (roadmap or {}).get("actions", []),
        }
