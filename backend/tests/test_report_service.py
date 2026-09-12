from decimal import Decimal

from app.services.report_service import ReportService


def test_calculation_csv_contains_summary_and_breakdown() -> None:
    class Breakdown:
        category = "energy"
        source = "grid"
        activity_quantity = Decimal("100")
        activity_unit = "kwh"
        applied_factor = Decimal("0.4")
        kg_co2e = Decimal("40")
        percentage_of_total = Decimal("100")

    class Calculation:
        id = 4
        total_kg_co2e = Decimal("40")
        breakdown = [Breakdown()]

    class Calculations:
        def get_calculation(self, calculation_id: int):
            return Calculation() if calculation_id == 4 else None

    content = ReportService(Calculations()).calculation_csv(4)
    assert content is not None
    assert "summary,4,,,,,,40,100" in content
    assert "breakdown,4,energy,grid,100,kwh,0.4,40,100" in content
    assert ReportService(Calculations()).calculation_csv(99) is None
