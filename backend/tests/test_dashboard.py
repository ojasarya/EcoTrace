from decimal import Decimal

from app.domain.hotspots import Hotspot
from app.services.dashboard_service import DashboardService


def test_dashboard_returns_empty_summary_without_calculations() -> None:
    class Calculations:
        def list_calculations(self, factory_id: int):
            return []

    service = DashboardService(Calculations(), None, None, None)
    dashboard = service.get_factory_dashboard(7)
    assert dashboard["factory_id"] == 7
    assert dashboard["calculation_id"] is None
    assert dashboard["categories"] == []


def test_dashboard_groups_latest_calculation_categories() -> None:
    class Calculation:
        id = 3
        total_kg_co2e = Decimal("100")
        breakdown = [
            type("Breakdown", (), {"category": "energy", "kg_co2e": Decimal("70")})(),
            type("Breakdown", (), {"category": "energy", "kg_co2e": Decimal("10")})(),
            type("Breakdown", (), {"category": "waste", "kg_co2e": Decimal("20")})(),
        ]

    class Calculations:
        def list_calculations(self, factory_id: int):
            return [Calculation()]

    class Hotspots:
        def get_hotspots(self, calculation_id: int):
            return ()

    class Interventions:
        def rank_recommendations(self, hotspots):
            return []

    class Roadmap:
        def build(self, calculation_id: int):
            return {"actions": []}

    dashboard = DashboardService(
        Calculations(), Hotspots(), Interventions(), Roadmap()
    ).get_factory_dashboard(7)
    assert dashboard["total_kg_co2e"] == Decimal("100")
    assert dashboard["categories"][0]["kg_co2e"] == Decimal("80")
    assert dashboard["categories"][1]["percentage_of_total"] == Decimal("20")
