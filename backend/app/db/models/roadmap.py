"""Persisted roadmap action tracking model."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class RoadmapAction(TimestampMixin, Base):
    """A recommendation selected for execution at a factory."""

    __tablename__ = "roadmap_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    calculation_id: Mapped[int] = mapped_column(
        ForeignKey("emission_calculations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    intervention_id: Mapped[int] = mapped_column(
        ForeignKey("interventions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned")
    planned_start_date: Mapped[date | None] = mapped_column(Date)
    owner: Mapped[str | None] = mapped_column(String(150))
    actual_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    actual_reduction_kg_co2e: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
