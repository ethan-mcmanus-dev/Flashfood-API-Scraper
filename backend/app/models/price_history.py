"""
Price history model for tracking product price changes over time.

Enables trend analysis and price drop alerts.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class PriceHistory(Base):
    """
    Historical price tracking model.

    Records price changes for products to enable:
    - Price trend visualization
    - Price drop alerts
    - Deal quality analysis

    Attributes:
        id: Primary key
        product_id: Foreign key to product table
        price: Recorded price at this timestamp
        quantity_available: Stock level at this timestamp
        recorded_at: When this price was observed
    """

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity_available = Column(Integer, default=0, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="price_history")
