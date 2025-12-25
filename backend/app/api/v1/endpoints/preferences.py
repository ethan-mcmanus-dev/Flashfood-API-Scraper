"""
User preference endpoints for managing notification settings.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.product import Product
from app.models.store import Store
from app.schemas.preference import UserPreferenceResponse, UserPreferenceUpdate
from app.services.notification import notification_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=UserPreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPreference:
    """
    Get current user's notification preferences.

    Parameters:
        db: Database session
        current_user: Authenticated user

    Returns:
        User preference settings

    Raises:
        HTTPException: If preferences not found
    """
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found",
        )

    return preferences


@router.patch("/", response_model=UserPreferenceResponse)
async def update_preferences(
    preference_update: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPreference:
    """
    Update user's notification preferences.

    Parameters:
        preference_update: Updated preference values
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated preferences

    Raises:
        HTTPException: If preferences not found
    """
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == current_user.id)
        .first()
    )

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found",
        )

    # Update only provided fields
    update_data = preference_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    try:
        db.commit()
        db.refresh(preferences)
        logger.info(f"Updated preferences for user {current_user.email}")
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

    return preferences
