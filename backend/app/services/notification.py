"""
Notification service for sending personalized deal alerts to users.

Checks user preferences against new deals and sends notifications via email.
"""

import logging
from datetime import datetime, time, timezone
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.product import Product
from app.models.store import Store
from app.services.email import EmailService

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending personalized deal notifications to users.
    
    Filters deals based on user preferences and sends notifications
    during specified time windows.
    """

    def __init__(self):
        """Initialize notification service."""
        self.email_service = EmailService()

    def is_notification_time_allowed(self, preferences: UserPreference) -> bool:
        """
        Check if current time is within user's notification window.
        
        Args:
            preferences: User preference settings
            
        Returns:
            True if notifications are allowed at current time
        """
        now = datetime.now(timezone.utc).time()
        start_time = preferences.notification_start_time
        end_time = preferences.notification_end_time
        
        # Handle case where notification window crosses midnight
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:
            return now >= start_time or now <= end_time

    def filter_deals_for_user(
        self, 
        deals: List[Product], 
        preferences: UserPreference,
        db: Session
    ) -> List[Product]:
        """
        Filter deals based on user preferences.
        
        Args:
            deals: List of all available deals
            preferences: User preference settings
            db: Database session
            
        Returns:
            List of deals matching user preferences
        """
        filtered_deals = []
        
        for deal in deals:
            # Check city match
            if deal.store.city != preferences.city:
                continue
                
            # Check store selection (if user has specific stores selected)
            if preferences.selected_store_ids and deal.store_id not in preferences.selected_store_ids:
                continue
                
            # Check minimum discount
            if deal.discount_percent and deal.discount_percent < preferences.min_discount_percent:
                continue
                
            # Check favorite categories (if user has specified favorites)
            if preferences.favorite_categories and deal.category not in preferences.favorite_categories:
                continue
                
            filtered_deals.append(deal)
            
        return filtered_deals

    async def send_new_deal_notifications(self, new_deals: List[Product], db: Session) -> int:
        """
        Send notifications to users about new deals matching their preferences.
        
        Args:
            new_deals: List of newly discovered deals
            db: Database session
            
        Returns:
            Number of notifications sent
        """
        if not new_deals:
            return 0
            
        logger.info(f"Processing {len(new_deals)} new deals for notifications")
        
        # Get all users with email notifications enabled
        users_with_notifications = (
            db.query(User)
            .join(UserPreference, User.id == UserPreference.user_id)
            .filter(UserPreference.email_notifications == True)
            .filter(UserPreference.notify_new_deals == True)
            .all()
        )
        
        notifications_sent = 0
        
        for user in users_with_notifications:
            try:
                preferences = user.preferences
                
                # Skip if user has no preferences
                if not preferences:
                    logger.debug(f"Skipping notification for {user.email} - no preferences set")
                    continue
                
                # Check if it's within the user's notification time window
                if not self.is_notification_time_allowed(preferences):
                    logger.debug(f"Skipping notification for {user.email} - outside time window")
                    continue
                
                # Filter deals based on user preferences
                user_deals = self.filter_deals_for_user(new_deals, preferences, db)
                
                if not user_deals:
                    logger.debug(f"No matching deals for {user.email}")
                    continue
                
                # Convert deals to dict format for email
                deals_data = []
                for deal in user_deals:
                    deals_data.append({
                        "name": deal.name,
                        "description": deal.description,
                        "category": deal.category,
                        "original_price": deal.original_price,
                        "discount_price": deal.discount_price,
                        "discount_percent": deal.discount_percent,
                        "quantity_available": deal.quantity_available,
                        "expiry_date": deal.expiry_date.isoformat() if deal.expiry_date else None,
                        "store_name": deal.store.name,
                        "store_city": deal.store.city,
                    })
                
                # Send email notification
                success = await self.email_service.send_new_deal_alert(
                    to_email=user.email,
                    user_name=user.full_name or user.email,
                    deals=deals_data
                )
                
                if success:
                    notifications_sent += 1
                    logger.info(f"Sent notification to {user.email} for {len(user_deals)} deals")
                else:
                    logger.warning(f"Failed to send notification to {user.email}")
                    
            except Exception as e:
                logger.error(f"Error processing notifications for user {user.email}: {e}")
                continue
        
        logger.info(f"Sent {notifications_sent} deal notifications")
        return notifications_sent

    async def send_price_drop_notifications(self, price_drops: List[Dict[str, Any]], db: Session) -> int:
        """
        Send notifications to users about price drops on items they're interested in.
        
        Args:
            price_drops: List of price drop events
            db: Database session
            
        Returns:
            Number of notifications sent
        """
        if not price_drops:
            return 0
            
        logger.info(f"Processing {len(price_drops)} price drops for notifications")
        
        # Get all users with price drop notifications enabled
        users_with_notifications = (
            db.query(User)
            .join(UserPreference, User.id == UserPreference.user_id)
            .filter(UserPreference.email_notifications == True)
            .filter(UserPreference.notify_price_drops == True)
            .all()
        )
        
        notifications_sent = 0
        
        for user in users_with_notifications:
            try:
                preferences = user.preferences
                
                # Skip if user has no preferences
                if not preferences:
                    continue
                
                # Check if it's within the user's notification time window
                if not self.is_notification_time_allowed(preferences):
                    continue
                
                # Filter price drops based on user preferences
                user_price_drops = []
                for drop in price_drops:
                    product = drop["product"]
                    
                    # Apply same filtering logic as new deals
                    if (product.store.city == preferences.city and
                        (not preferences.selected_store_ids or product.store_id in preferences.selected_store_ids) and
                        (not preferences.favorite_categories or product.category in preferences.favorite_categories)):
                        user_price_drops.append(drop)
                
                if not user_price_drops:
                    continue
                
                # Send price drop notifications (one per product for now)
                for drop in user_price_drops:
                    product = drop["product"]
                    old_price = drop["old_price"]
                    new_price = drop["new_price"]
                    
                    success = await self.email_service.send_price_drop_alert(
                        to_email=user.email,
                        user_name=user.full_name or user.email,
                        product_name=product.name,
                        old_price=old_price,
                        new_price=new_price,
                        store_name=product.store.name
                    )
                    
                    if success:
                        notifications_sent += 1
                        
            except Exception as e:
                logger.error(f"Error processing price drop notifications for user {user.email}: {e}")
                continue
        
        logger.info(f"Sent {notifications_sent} price drop notifications")
        return notifications_sent

    async def send_preference_test_email(
        self, 
        user: User, 
        products: List[Product], 
        preferences: UserPreference
    ) -> bool:
        """
        Send a test email with current deals matching user preferences.
        
        Args:
            user: User to send email to
            products: List of matching products
            preferences: User's current preferences
            
        Returns:
            True if email sent successfully
        """
        try:
            if not products:
                # Send email saying no matches found
                success = await self.email_service.send_preference_test_no_matches(
                    to_email=user.email,
                    user_name=user.full_name or user.email,
                    preferences_summary={
                        "city": preferences.city,
                        "min_discount": preferences.min_discount_percent,
                        "categories": preferences.favorite_categories or [],
                        "store_count": len(preferences.selected_store_ids) if preferences.selected_store_ids else 0
                    }
                )
            else:
                # Convert products to dict format for email
                deals_data = []
                for product in products:
                    deals_data.append({
                        "name": product.name,
                        "description": product.description,
                        "category": product.category,
                        "original_price": product.original_price,
                        "discount_price": product.discount_price,
                        "discount_percent": product.discount_percent,
                        "quantity_available": product.quantity_available,
                        "expiry_date": product.expiry_date.isoformat() if product.expiry_date else None,
                        "store_name": product.store.name,
                        "store_city": product.store.city,
                    })
                
                success = await self.email_service.send_preference_test_matches(
                    to_email=user.email,
                    user_name=user.full_name or user.email,
                    deals=deals_data,
                    preferences_summary={
                        "city": preferences.city,
                        "min_discount": preferences.min_discount_percent,
                        "categories": preferences.favorite_categories or [],
                        "store_count": len(preferences.selected_store_ids) if preferences.selected_store_ids else 0
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending preference test email to {user.email}: {e}")
            return False


# Global notification service instance
notification_service = NotificationService()