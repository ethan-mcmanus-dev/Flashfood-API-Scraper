"""
Pydantic schemas for user preference API requests and responses.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserPreferenceBase(BaseModel):
    """Base user preference schema."""

    city: str = Field(..., description="Preferred city (calgary, vancouver, etc.)")
    max_distance_km: float = Field(75.0, ge=1, le=200, description="Maximum distance from city center")
    email_notifications: bool = Field(True, description="Enable email notifications")
    notify_new_deals: bool = Field(True, description="Notify when new deals appear")
    notify_price_drops: bool = Field(False, description="Notify when prices drop")
    min_discount_percent: int = Field(0, ge=0, le=100, description="Minimum discount to notify")
    favorite_categories: Optional[List[str]] = Field(None, description="Preferred product categories")


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""

    pass


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)."""

    city: Optional[str] = None
    max_distance_km: Optional[float] = Field(None, ge=1, le=200)
    email_notifications: Optional[bool] = None
    notify_new_deals: Optional[bool] = None
    notify_price_drops: Optional[bool] = None
    min_discount_percent: Optional[int] = Field(None, ge=0, le=100)
    favorite_categories: Optional[List[str]] = None


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference API responses."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
