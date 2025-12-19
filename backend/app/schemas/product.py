"""
Pydantic schemas for product-related API requests and responses.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base product schema."""

    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    original_price: Optional[float] = Field(None, ge=0)
    discount_price: float = Field(..., ge=0)
    discount_percent: Optional[int] = Field(None, ge=0, le=100)
    quantity_available: int = Field(0, ge=0)
    expiry_date: Optional[datetime] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    store_id: int
    external_id: str


class ProductResponse(ProductBase):
    """Schema for product API responses."""

    id: int
    store_id: int
    external_id: str
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True


class ProductWithStore(ProductResponse):
    """Product response including store information."""

    store_name: str
    store_address: Optional[str] = None
    store_city: str


class PriceHistoryPoint(BaseModel):
    """Single price history data point."""

    price: float
    quantity_available: int
    recorded_at: datetime

    class Config:
        from_attributes = True


class ProductWithHistory(ProductResponse):
    """Product response including price history."""

    price_history: List[PriceHistoryPoint] = []
