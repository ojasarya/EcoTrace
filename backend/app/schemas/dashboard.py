"""API schemas for factory dashboard summaries."""

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.hotspot import HotspotRead
from app.schemas.intervention import RecommendationRead
from app.schemas.roadmap import RoadmapActionRead


class DashboardCategoryRead(BaseModel):
    category: str
    kg_co2e: Decimal
    percentage_of_total: Decimal


class DashboardRead(BaseModel):
    factory_id: int
    calculation_id: int | None
    total_kg_co2e: Decimal
    categories: list[DashboardCategoryRead]
    hotspots: list[HotspotRead]
    recommendations: list[RecommendationRead]
    roadmap: list[RoadmapActionRead]
