from decimal import Decimal

from app.domain.hotspots import Hotspot
from app.services.roadmap_service import RoadmapService


def test_roadmap_sequences_actions_and_accumulates_totals() -> None:
    class Hotspots:
        def get_hotspots(self, calculation_id: int):
            return (
                Hotspot("energy", "grid", Decimal("70"), Decimal("70"), "high", 1, ""),
                Hotspot("waste", "landfill", Decimal("30"), Decimal("30"), "moderate", 2, ""),
            )

    class Interventions:
        def rank_recommendations(self, hotspots):
            class Intervention:
                def __init__(self, id, name, cost):
                    self.id, self.name, self.estimated_cost = id, name, cost

            return [
                (Intervention(1, "Renewable power", Decimal("1000")), hotspots[0], "first", Decimal("35"), Decimal("1"), None),
                (Intervention(2, "Recycling", Decimal("500")), hotspots[1], "second", Decimal("15"), Decimal("1"), None),
            ]

    roadmap = RoadmapService(Hotspots(), Interventions()).build(9)
    assert roadmap["total_actions"] == 2
    assert roadmap["total_estimated_cost"] == Decimal("1500")
    assert roadmap["actions"][1]["cumulative_reduction_kg_co2e"] == Decimal("50")
