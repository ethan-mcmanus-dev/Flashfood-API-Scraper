"""
User preference model for notification settings and filters.

Stores user-specific configuration for alerts and deal filtering.
"""

from datetime import datetime, timezone, time

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, JSON, Time
from sqlalchemy.orm import relationship

from app.db.database import Base


class UserPreference(Base):
    """
    User notification and filter preferences.

    Controls what deals users see and how they're notified.

    Attributes:
        id: Primary key
        user_id: Foreign key to user table
        city: Preferred city for deal searches
        max_distance_km: Maximum distance from city center
        selected_store_ids: JSON array of specific store IDs to monitor
        email_notifications: Enable/disable email alerts
        web_push_notifications: Enable/disable web push notifications
        notify_new_deals: Alert on any new deal
        notify_price_drops: Alert on price reductions
        min_discount_percent: Only notify for discounts above this threshold
        favorite_categories: JSON array of preferred product categories
        excluded_categories: JSON array of categories to exclude
        notification_start_time: Start time for notifications (e.g., 5:00 AM)
        notification_end_time: End time for notifications (e.g., 10:00 PM)
        created_at: When preferences were created
        updated_at: Last preference update
    """

    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    city = Column(String, nullable=False, default="calgary")
    max_distance_km = Column(Float, nullable=False, default=75.0)
    selected_store_ids = Column(JSON, default=list, nullable=True)  # Specific stores to monitor
    email_notifications = Column(Boolean, default=True, nullable=False)
    web_push_notifications = Column(Boolean, default=False, nullable=False)  # New: web push
    notify_new_deals = Column(Boolean, default=True, nullable=False)
    notify_price_drops = Column(Boolean, default=False, nullable=False)
    min_discount_percent = Column(Integer, default=0, nullable=False)
    favorite_categories = Column(JSON, default=list, nullable=True)
    excluded_categories = Column(JSON, default=list, nullable=True)  # New: categories to exclude
    notification_start_time = Column(Time, default=time(5, 0), nullable=False)  # 5:00 AM
    notification_end_time = Column(Time, default=time(22, 0), nullable=False)   # 10:00 PM
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="preferences")
