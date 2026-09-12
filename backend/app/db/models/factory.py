"""Factory and reporting-period persistence models."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Factory(TimestampMixin, Base):
    """An industrial facility managed by EcoTrace."""

    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    industry_type: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    production_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reporting_periods: Mapped[list["ReportingPeriod"]] = relationship(
        back_populates="factory",
        cascade="all, delete-orphan",
    )


class ReportingPeriod(TimestampMixin, Base):
    """A time window for a factory's operational and emissions data."""

    __tablename__ = "reporting_periods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    factory_id: Mapped[int] = mapped_column(
        ForeignKey("factories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    production_quantity: Mapped[float] = mapped_column(nullable=False)
    production_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    factory: Mapped[Factory] = relationship(back_populates="reporting_periods")
    production_activities: Mapped[list["ProductionActivity"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
    energy_usage: Mapped[list["EnergyUsage"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
    material_usage: Mapped[list["MaterialUsage"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
    waste_records: Mapped[list["WasteRecord"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
    transportation_activities: Mapped[list["TransportationActivity"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
    calculations: Mapped[list["EmissionCalculation"]] = relationship(
        back_populates="reporting_period",
        cascade="all, delete-orphan",
    )
