"""API schemas for factories and reporting periods."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FactoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    industry_type: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=200)
    production_unit: str = Field(min_length=1, max_length=50)


class FactoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    industry_type: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    production_unit: str | None = Field(default=None, min_length=1, max_length=50)


class FactoryRead(FactoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ReportingPeriodCreate(BaseModel):
    period_start: date
    period_end: date
    production_quantity: Decimal = Field(ge=0)
    production_unit: str = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_date_range(self) -> "ReportingPeriodCreate":
        if self.period_end < self.period_start:
            raise ValueError("period_end must not be before period_start")
        return self


class ReportingPeriodRead(ReportingPeriodCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factory_id: int
