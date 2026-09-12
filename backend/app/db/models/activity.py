"""Factory activity persistence models."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductionActivity(Base):
    __tablename__ = "production_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    process_name: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="production_activities"
    )


class EnergyUsage(Base):
    __tablename__ = "energy_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    renewable_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
    )

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="energy_usage"
    )


class MaterialUsage(Base):
    __tablename__ = "material_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_name: Mapped[str] = mapped_column(String(150), nullable=False)
    material_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    recycled_content_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0"),
    )

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="material_usage"
    )


class WasteRecord(Base):
    __tablename__ = "waste_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    waste_type: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    disposal_method: Mapped[str] = mapped_column(String(100), nullable=False)
    recycled_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
        default=Decimal("0"),
    )

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="waste_records"
    )


class TransportationActivity(Base):
    __tablename__ = "transportation_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_periods.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(String(100), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)
    distance: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    distance_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    load_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    load_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    reporting_period: Mapped["ReportingPeriod"] = relationship(
        back_populates="transportation_activities"
    )
