"""Intervention catalog and hotspot matching service."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.intervention import Intervention
from app.domain.hotspots import Hotspot


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

    def match(self, hotspots: tuple[Hotspot, ...]) -> list[tuple[Intervention, Hotspot, str]]:
        interventions = self.list_interventions()
        matches: list[tuple[Intervention, Hotspot, str]] = []
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
                    matches.append((intervention, hotspot, rationale))
        return matches
