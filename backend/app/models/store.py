"""
Store model representing Flashfood partner locations.

Tracks store information, location, and associated products.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Store(Base):
    """
    Physical store location model.

    Attributes:
        id: Primary key
        external_id: Flashfood's store identifier
        name: Store name (e.g., "No Frills Northland Village")
        address: Full street address
        city: City name for filtering
        latitude: GPS coordinate for distance calculations
        longitude: GPS coordinate for distance calculations
        created_at: First time store was discovered
        updated_at: Last time store data was refreshed
    """

    __tablename__ = "store"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    products = relationship("Product", back_populates="store", cascade="all, delete-orphan")
