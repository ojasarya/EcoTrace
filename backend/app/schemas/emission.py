"""API schemas for emission factors and calculation results."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EmissionFactorCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=150)
    unit: str = Field(min_length=1, max_length=50)
    kg_co2e_per_unit: Decimal = Field(ge=0)
    geography: str = Field(min_length=1, max_length=100)
    source_reference: str = Field(min_length=1)
    valid_from: date
    valid_to: date | None = None
    version: str = Field(min_length=1, max_length=50)


class EmissionFactorRead(EmissionFactorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EmissionBreakdownRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    calculation_id: int
    category: str
    source: str
    activity_quantity: Decimal
    activity_unit: str
    applied_factor: Decimal
    kg_co2e: Decimal
    percentage_of_total: Decimal
    explanation: str | None


class EmissionCalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporting_period_id: int
    total_kg_co2e: Decimal
    calculation_version: str
    status: str
    breakdown: list[EmissionBreakdownRead]
