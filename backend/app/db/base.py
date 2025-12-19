"""
Import all models here for Alembic migration auto-generation.

This ensures all models are registered with SQLAlchemy Base.
"""

from app.db.database import Base  # noqa
from app.models.user import User  # noqa
from app.models.store import Store  # noqa
from app.models.product import Product  # noqa
from app.models.price_history import PriceHistory  # noqa
from app.models.user_preference import UserPreference  # noqa
