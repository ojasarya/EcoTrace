"""Calculation report generation service."""

import csv
from io import StringIO

from app.services.emission_calculation_service import EmissionCalculationService


class ReportService:
    """Generate downloadable representations of persisted calculations."""

    def __init__(self, calculation_service: EmissionCalculationService) -> None:
        self.calculation_service = calculation_service

    def calculation_csv(self, calculation_id: int) -> str | None:
        calculation = self.calculation_service.get_calculation(calculation_id)
        if calculation is None:
            return None

        output = StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(
            [
                "row_type",
                "calculation_id",
                "category",
                "source",
                "activity_quantity",
                "activity_unit",
                "applied_factor",
                "kg_co2e",
                "percentage_of_total",
            ]
        )
        writer.writerow(
            [
                "summary",
                calculation.id,
                "",
                "",
                "",
                "",
                "",
                calculation.total_kg_co2e,
                "100",
            ]
        )
        for item in calculation.breakdown:
            writer.writerow(
                [
                    "breakdown",
                    calculation.id,
                    item.category,
                    item.source,
                    item.activity_quantity,
                    item.activity_unit,
                    item.applied_factor,
                    item.kg_co2e,
                    item.percentage_of_total,
                ]
            )
        return output.getvalue()
