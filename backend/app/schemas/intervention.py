"""API schemas for circular interventions and recommendations."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InterventionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    target_source: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)
    estimated_cost: Decimal = Field(ge=0)
    estimated_reduction_percentage: Decimal = Field(ge=0, le=100)
    feasibility: str = Field(min_length=1, max_length=30)
    urgency: str = Field(min_length=1, max_length=30)


class InterventionRead(InterventionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RecommendationRead(InterventionRead):
    hotspot_rank: int
    hotspot_source: str
    hotspot_percentage: Decimal
    rationale: str
