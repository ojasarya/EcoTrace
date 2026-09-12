"""API schemas for persisted roadmap actions."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RoadmapActionCreate(BaseModel):
    calculation_id: int = Field(gt=0)
    intervention_id: int = Field(gt=0)
    status: str = Field(default="planned", min_length=1, max_length=30)
    planned_start_date: date | None = None
    owner: str | None = Field(default=None, max_length=150)
    actual_cost: Decimal | None = Field(default=None, ge=0)
    actual_reduction_kg_co2e: Decimal | None = Field(default=None, ge=0)


class RoadmapActionUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=30)
    planned_start_date: date | None = None
    owner: str | None = Field(default=None, max_length=150)
    actual_cost: Decimal | None = Field(default=None, ge=0)
    actual_reduction_kg_co2e: Decimal | None = Field(default=None, ge=0)


class RoadmapActionRead(RoadmapActionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factory_id: int
