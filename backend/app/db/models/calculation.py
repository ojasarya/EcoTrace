"""Emission calculation persistence models."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class EmissionCalculation(TimestampMixin, Base):
    __tablename__ = "emission_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    total_kg_co2e: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )
    calculation_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="completed")

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="calculations"
    )
    breakdown: Mapped[list["EmissionBreakdown"]] = relationship(
        back_populates="calculation",
        cascade="all, delete-orphan",
    )


class EmissionBreakdown(Base):
    __tablename__ = "emission_breakdowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    calculation_id: Mapped[int] = mapped_column(
        ForeignKey("emission_calculations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(150), nullable=False)
    activity_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    activity_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    applied_factor: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    kg_co2e: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    percentage_of_total: Mapped[Decimal] = mapped_column(
        Numeric(7, 4),
        nullable=False,
    )
    explanation: Mapped[str | None] = mapped_column(Text)

    calculation: Mapped[EmissionCalculation] = relationship(
        back_populates="breakdown"
    )
