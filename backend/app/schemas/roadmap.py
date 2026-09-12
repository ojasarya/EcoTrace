"""API schemas for prioritized emission-reduction roadmaps."""

from decimal import Decimal

from pydantic import BaseModel


class RoadmapActionRead(BaseModel):
    sequence: int
    recommendation_rank: int
    intervention_id: int
    intervention_name: str
    target_source: str
    phase: str
    estimated_cost: Decimal
    estimated_reduction_kg_co2e: Decimal
    cumulative_cost: Decimal
    cumulative_reduction_kg_co2e: Decimal
    rationale: str


class RoadmapRead(BaseModel):
    calculation_id: int
    total_actions: int
    total_estimated_cost: Decimal
    total_estimated_reduction_kg_co2e: Decimal
    actions: list[RoadmapActionRead]
