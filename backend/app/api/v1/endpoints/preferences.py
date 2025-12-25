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

    db.commit()
    db.refresh(preferences)

    # TEMPORARY: Send test email with matching deals if email notifications are enabled
    if preferences.email_notifications:
        try:
            logger.info("Sending test email with current matching deals...")
            
            # Get matching products based on updated preferences
            query = db.query(Product).join(Store)
            
            # Filter by city
            if preferences.city:
                query = query.filter(Store.city == preferences.city)
            
            # Filter by selected stores
            if preferences.selected_store_ids:
                query = query.filter(Store.id.in_(preferences.selected_store_ids))
            
            # Filter by minimum discount
            if preferences.min_discount_percent:
                query = query.filter(Product.discount_percent >= preferences.min_discount_percent)
            
            # Filter by favorite categories
            if preferences.favorite_categories:
                query = query.filter(Product.category.in_(preferences.favorite_categories))
            
            # Only active products with quantity > 0
            query = query.filter(Product.quantity_available > 0)
            
            matching_products = query.limit(20).all()  # Limit to 20 for email
            
            if matching_products:
                # Send email with matching deals
                await notification_service.send_preference_test_email(
                    user=current_user,
                    products=matching_products,
                    preferences=preferences
                )
                logger.info(f"Sent test email to {current_user.email} with {len(matching_products)} matching deals")
            else:
                # Send email saying no matches found
                await notification_service.send_preference_test_email(
                    user=current_user,
                    products=[],
                    preferences=preferences
                )
                logger.info(f"Sent test email to {current_user.email} - no matching deals found")
                
        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            # Don't fail the preference update if email fails

    return preferences
