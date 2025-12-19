"""
Pydantic schemas for store-related API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    """Base store schema."""

    name: str
    address: Optional[str] = None
    city: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class StoreCreate(StoreBase):
    """Schema for creating a new store."""

    external_id: str


class StoreResponse(StoreBase):
    """Schema for store API responses."""

    id: int
    external_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoreWithDistance(StoreResponse):
    """Store response with calculated distance from user location."""

    distance_km: float = Field(..., description="Distance from user in kilometers")
