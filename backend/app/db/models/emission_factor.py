"""Emission-factor persistence model."""

from datetime import date

from sqlalchemy import Date, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class EmissionFactor(TimestampMixin, Base):
    __tablename__ = "emission_factors"
    __table_args__ = (
        UniqueConstraint(
            "category",
            "source",
            "unit",
            "version",
            name="uq_emission_factor_identity",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(150), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    kg_co2e_per_unit: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    geography: Mapped[str] = mapped_column(String(100), nullable=False)
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
