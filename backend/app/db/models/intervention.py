"""Persisted circular intervention catalog models."""

from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Intervention(TimestampMixin, Base):
    """A circular alternative that can address an emission source."""

    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_source: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    estimated_reduction_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )
    feasibility: Mapped[str] = mapped_column(String(30), nullable=False)
    urgency: Mapped[str] = mapped_column(String(30), nullable=False)
