"""API schemas for emission hotspots."""

from decimal import Decimal

from pydantic import BaseModel


class HotspotRead(BaseModel):
    category: str
    source: str
    kg_co2e: Decimal
    percentage_of_total: Decimal
    severity: str
    rank: int
    explanation: str
