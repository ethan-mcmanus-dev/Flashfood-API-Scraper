"""
Pydantic schemas for user preference API requests and responses.
"""

from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field


class UserPreferenceBase(BaseModel):
    """Base user preference schema."""

    city: str = Field(..., description="Preferred city (calgary, vancouver, etc.)")
    max_distance_km: float = Field(75.0, ge=1, le=200, description="Maximum distance from city center")
    selected_store_ids: Optional[List[int]] = Field(None, description="Specific store IDs to monitor")
    email_notifications: bool = Field(True, description="Enable email notifications")
    web_push_notifications: bool = Field(False, description="Enable web push notifications")
    notify_new_deals: bool = Field(True, description="Notify when new deals appear")
    notify_price_drops: bool = Field(False, description="Notify when prices drop")
    min_discount_percent: int = Field(0, ge=0, le=100, description="Minimum discount to notify")
    favorite_categories: Optional[List[str]] = Field(None, description="Preferred product categories")
    notification_start_time: time = Field(time(5, 0), description="Start time for notifications")
    notification_end_time: time = Field(time(22, 0), description="End time for notifications")


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences."""

    pass


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)."""

    city: Optional[str] = None
    max_distance_km: Optional[float] = Field(None, ge=1, le=200)
    selected_store_ids: Optional[List[int]] = None
    email_notifications: Optional[bool] = None
    web_push_notifications: Optional[bool] = None
    notify_new_deals: Optional[bool] = None
    notify_price_drops: Optional[bool] = None
    min_discount_percent: Optional[int] = Field(None, ge=0, le=100)
    favorite_categories: Optional[List[str]] = None
    notification_start_time: Optional[time] = None
    notification_end_time: Optional[time] = None


class UserPreferenceResponse(UserPreferenceBase):
    """Schema for user preference API responses."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
