"""Persistence service for emission factors."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.emission_factor import EmissionFactor
from app.db.transactions import commit_or_rollback


class EmissionFactorService:
    """Manage versioned emission factors."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_factor(self, **values: object) -> EmissionFactor:
        factor = EmissionFactor(**values)
        self.session.add(factor)
        commit_or_rollback(self.session)
        self.session.refresh(factor)
        return factor

    def list_factors(self) -> list[EmissionFactor]:
        return list(
            self.session.scalars(
                select(EmissionFactor).order_by(
                    EmissionFactor.category,
                    EmissionFactor.source,
                    EmissionFactor.version,
                )
            )
        )
