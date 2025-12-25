"""
User preference endpoints for managing notification settings.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db, SessionLocal
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

    # Send email in background task (don't await - let it run separately)
    if preferences.email_notifications:
        import asyncio
        asyncio.create_task(send_preference_email_background(current_user.id, preferences.id))
        logger.info(f"Scheduled background email task for user {current_user.email}")

    return preferences


async def send_preference_email_background(user_id: int, preference_id: int):
    """
    Background task to send preference update email.
    Runs separately from the main request to avoid blocking.
    """
    try:
        # Create new database session for background task
        db = SessionLocal()
        
        # Get fresh user and preferences data
        user = db.query(User).filter(User.id == user_id).first()
        preferences = db.query(UserPreference).filter(UserPreference.id == preference_id).first()
        
        if not user or not preferences:
            logger.error("User or preferences not found in background email task")
            return
            
        logger.info(f"Sending preference update email to {user.email}...")
        
        # Get matching products based on preferences
        query = db.query(Product).join(Store)
        
        # Filter by city
        if preferences.city:
            query = query.filter(Store.city == preferences.city)
        
        # Filter by selected stores (if any selected)
        if preferences.selected_store_ids:
            query = query.filter(Store.id.in_(preferences.selected_store_ids))
        
        # Filter by minimum discount
        if preferences.min_discount_percent and preferences.min_discount_percent > 0:
            query = query.filter(Product.discount_percent >= preferences.min_discount_percent)
        
        # Filter by favorite categories (if any selected)
        if preferences.favorite_categories:
            query = query.filter(Product.category.in_(preferences.favorite_categories))
        
        # Only active products with quantity > 0
        query = query.filter(Product.quantity_available > 0)
        
        matching_products = query.limit(10).all()  # Limit to 10 for email
        
        # Send email with matching deals
        await notification_service.send_preference_test_email(
            user=user,
            products=matching_products,
            preferences=preferences
        )
        logger.info(f"Successfully sent background email to {user.email} with {len(matching_products)} matching deals")
        
    except Exception as e:
        logger.error(f"Failed to send background preference email: {e}")
    finally:
        if 'db' in locals():
            db.close()
