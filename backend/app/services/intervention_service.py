"""Intervention catalog and hotspot matching service."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.intervention import Intervention
from app.domain.hotspots import Hotspot
from app.domain.recommendations import calculate_carbon_roi


class InterventionService:
    """Manage interventions and match them to calculated hotspots."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_intervention(self, **values: object) -> Intervention:
        intervention = Intervention(**values)
        self.session.add(intervention)
        self.session.commit()
        self.session.refresh(intervention)
        return intervention

    def list_interventions(self) -> list[Intervention]:
        return list(
            self.session.scalars(select(Intervention).order_by(Intervention.name))
        )

    def rank_recommendations(
        self, hotspots: tuple[Hotspot, ...]
    ) -> list[tuple[Intervention, Hotspot, str, Decimal, Decimal, Decimal | None]]:
        interventions = self.list_interventions()
        matches: list[
            tuple[Intervention, Hotspot, str, Decimal, Decimal, Decimal | None]
        ] = []
        for hotspot in hotspots:
            for intervention in interventions:
                if (
                    intervention.category.casefold() == hotspot.category.casefold()
                    and intervention.target_source.casefold()
                    == hotspot.source.casefold()
                ):
                    rationale = (
                        f"Targets {hotspot.source}, the rank {hotspot.rank} hotspot, "
                        f"responsible for {hotspot.percentage_of_total.normalize()}% "
                        "of total emissions."
                    )
                    reduction = (
                        hotspot.kg_co2e
                        * intervention.estimated_reduction_percentage
                        / Decimal("100")
                    )
                    carbon_roi = calculate_carbon_roi(
                        reduction, intervention.estimated_cost
                    )
                    feasibility_weight = {
                        "high": Decimal("1"),
                        "medium": Decimal("0.75"),
                        "low": Decimal("0.5"),
                    }.get(intervention.feasibility.casefold(), Decimal("0.5"))
                    urgency_weight = {
                        "high": Decimal("1"),
                        "medium": Decimal("0.75"),
                        "low": Decimal("0.5"),
                    }.get(intervention.urgency.casefold(), Decimal("0.5"))
                    cost = intervention.estimated_cost
                    score = (
                        hotspot.percentage_of_total
                        * intervention.estimated_reduction_percentage
                        * feasibility_weight
                        * urgency_weight
                        / (cost + Decimal("1"))
                    )
                    matches.append(
                        (intervention, hotspot, rationale, reduction, score, carbon_roi)
                    )
        return sorted(matches, key=lambda item: (-item[4], item[0].name.casefold()))
