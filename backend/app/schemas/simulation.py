"""API schemas for what-if emission simulations."""

from decimal import Decimal

from pydantic import BaseModel, Field


class SimulationAdjustment(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=150)
    reduction_percentage: Decimal = Field(ge=0, le=100)


class SimulationRequest(BaseModel):
    adjustments: list[SimulationAdjustment] = Field(min_length=1)


class SimulationBreakdownRead(BaseModel):
    category: str
    source: str
    simulated_kg_co2e: Decimal


class SimulationRead(BaseModel):
    calculation_id: int
    baseline_kg_co2e: Decimal
    simulated_kg_co2e: Decimal
    reduction_kg_co2e: Decimal
    reduction_percentage: Decimal
    breakdown: list[SimulationBreakdownRead]
