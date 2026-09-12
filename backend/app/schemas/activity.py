"""API schemas for factory activity inputs."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporting_period_id: int


class ProductionActivityCreate(BaseModel):
    process_name: str = Field(min_length=1, max_length=150)
    quantity: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=50)


class ProductionActivityRead(ActivityRead, ProductionActivityCreate):
    pass


class EnergyUsageCreate(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=50)
    renewable_percentage: Decimal = Field(default=0, ge=0, le=100)


class EnergyUsageRead(ActivityRead, EnergyUsageCreate):
    pass


class MaterialUsageCreate(BaseModel):
    material_name: str = Field(min_length=1, max_length=150)
    material_type: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=50)
    recycled_content_percentage: Decimal = Field(default=0, ge=0, le=100)


class MaterialUsageRead(ActivityRead, MaterialUsageCreate):
    pass


class WasteRecordCreate(BaseModel):
    waste_type: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=50)
    disposal_method: str = Field(min_length=1, max_length=100)
    recycled_quantity: Decimal = Field(default=0, ge=0)


class WasteRecordRead(ActivityRead, WasteRecordCreate):
    pass


class TransportationActivityCreate(BaseModel):
    mode: str = Field(min_length=1, max_length=100)
    direction: str = Field(min_length=1, max_length=50)
    distance: Decimal = Field(ge=0)
    distance_unit: str = Field(min_length=1, max_length=50)
    load_quantity: Decimal = Field(ge=0)
    load_unit: str = Field(min_length=1, max_length=50)


class TransportationActivityRead(ActivityRead, TransportationActivityCreate):
    pass
