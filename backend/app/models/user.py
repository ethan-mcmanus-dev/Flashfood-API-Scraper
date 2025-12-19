"""
User model for authentication and user management.

Stores user credentials and profile information.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """
    User account model.

    Attributes:
        id: Primary key
        email: Unique email address for authentication
        hashed_password: Bcrypt hashed password
        full_name: User's display name
        is_active: Account status flag
        is_superuser: Admin privilege flag
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")
