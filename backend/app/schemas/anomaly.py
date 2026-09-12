"""API schemas for emissions anomaly detection."""

from decimal import Decimal

from pydantic import BaseModel


class AnomalyRead(BaseModel):
    calculation_id: int
    total_kg_co2e: Decimal
    is_anomaly: bool
    anomaly_score: Decimal
    explanation: str
