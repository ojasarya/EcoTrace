"""Persistence service for selected roadmap actions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.calculation import EmissionCalculation
from app.db.models.intervention import Intervention
from app.db.models.factory import Factory
from app.db.models.roadmap import RoadmapAction


class RoadmapActionService:
    """Create, list, and update factory action tracking records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_action(self, factory_id: int, **values: object) -> RoadmapAction:
        calculation = self.session.scalar(
            select(EmissionCalculation)
            .join(EmissionCalculation.reporting_period)
            .where(
                EmissionCalculation.id == values["calculation_id"],
                EmissionCalculation.reporting_period.has(factory_id=factory_id),
            )
        )
        if calculation is None:
            raise ValueError("Calculation does not belong to factory")
        if self.session.get(Intervention, values["intervention_id"]) is None:
            raise ValueError("Intervention not found")
        action = RoadmapAction(factory_id=factory_id, **values)
        self.session.add(action)
        self.session.commit()
        self.session.refresh(action)
        return action

    def factory_exists(self, factory_id: int) -> bool:
        return self.session.get(Factory, factory_id) is not None

    def list_actions(self, factory_id: int) -> list[RoadmapAction]:
        return list(
            self.session.scalars(
                select(RoadmapAction)
                .where(RoadmapAction.factory_id == factory_id)
                .order_by(RoadmapAction.id)
            )
        )

    def update_action(self, action: RoadmapAction, **values: object) -> RoadmapAction:
        for key, value in values.items():
            setattr(action, key, value)
        self.session.commit()
        self.session.refresh(action)
        return action

    def get_action(self, factory_id: int, action_id: int) -> RoadmapAction | None:
        return self.session.scalar(
            select(RoadmapAction).where(
                RoadmapAction.id == action_id,
                RoadmapAction.factory_id == factory_id,
            )
        )
