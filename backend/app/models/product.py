"""
Product model representing individual items available at stores.

Tracks current deals, pricing, and availability.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.db.database import Base


class Product(Base):
    """
    Product deal model.

    Represents an item currently available for purchase at a discounted price.

    Attributes:
        id: Primary key
        store_id: Foreign key to store table
        external_id: Flashfood's product identifier
        name: Product name (e.g., "Assorted Bakery Items")
        description: Product description from Flashfood
        category: Product category (e.g., "Bakery", "Produce")
        original_price: Original retail price before discount
        discount_price: Current discounted price
        discount_percent: Calculated discount percentage
        quantity_available: Number of units in stock
        expiry_date: When the product expires
        image_url: URL to product image
        first_seen: When this product was first detected
        last_seen: Last time this product was still available
    """

    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("store.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)
    original_price = Column(Float, nullable=True)
    discount_price = Column(Float, nullable=False)
    discount_percent = Column(Integer, nullable=True)
    quantity_available = Column(Integer, default=0, nullable=False, index=True)  # Add index for filtering
    expiry_date = Column(DateTime, nullable=True)
    image_url = Column(String, nullable=True)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    store = relationship("Store", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for filtering by store and availability (most common query)
        Index('idx_product_store_quantity', 'store_id', 'quantity_available'),
        # Index for filtering by category and availability  
        Index('idx_product_category_quantity', 'category', 'quantity_available'),
        # Index for discount filtering
        Index('idx_product_discount', 'discount_percent', 'quantity_available'),
    )
