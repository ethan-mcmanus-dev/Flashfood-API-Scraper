"""
Notification endpoints for testing and managing user notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.product import Product
from app.services.notification import notification_service

router = APIRouter()


@router.post("/test")
async def test_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test notification system by sending a sample notification to the current user.
    
    This endpoint always sends a test email regardless of user preferences or available deals.
    """
    try:
        # Get some recent deals to use as test data, or create mock data if none exist
        recent_deals = (
            db.query(Product)
            .join(Product.store)
            .filter(Product.quantity_available > 0)
            .order_by(Product.last_seen.desc())
            .limit(3)
            .all()
        )
        
        # If no real deals exist, create mock test data
        if not recent_deals:
            test_deals_data = [
                {
                    "name": "Test Product 1 - Greek Yogurt",
                    "description": "Sample deal for testing notifications",
                    "category": "Dairy",
                    "original_price": 5.99,
                    "discount_price": 3.99,
                    "discount_percent": 33,
                    "quantity_available": 5,
                    "expiry_date": None,
                    "store_name": "Test Store",
                    "store_city": "Calgary",
                },
                {
                    "name": "Test Product 2 - Fresh Bread",
                    "description": "Another sample deal for testing",
                    "category": "Bakery",
                    "original_price": 4.49,
                    "discount_price": 2.99,
                    "discount_percent": 33,
                    "quantity_available": 3,
                    "expiry_date": None,
                    "store_name": "Test Store",
                    "store_city": "Calgary",
                }
            ]
        else:
            # Convert real deals to dict format for email
            test_deals_data = []
            for deal in recent_deals:
                test_deals_data.append({
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
        
        # Send test email directly using email service
        from app.services.email import email_service
        
        # Send to the actual user's email
        success = await email_service.send_new_deal_alert(
            to_email=current_user.email,
            user_name=current_user.full_name or current_user.email,
            deals=test_deals_data
        )
        
        return {
            "status": "success" if success else "warning",
            "message": f"Test notification sent to {current_user.email}" if success else f"Test notification failed for {current_user.email}",
            "email_sent": success,
            "test_deals_count": len(test_deals_data),
            "using_mock_data": len(recent_deals) == 0,
            "email_service": email_service.service
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.post("/send-manual")
async def send_manual_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger notifications for all users based on current deals.
    
    This endpoint processes all current deals and sends notifications to users
    whose preferences match the available deals.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger manual notifications"
        )
    
    try:
        # Get all current deals
        current_deals = (
            db.query(Product)
            .join(Product.store)
            .filter(Product.quantity_available > 0)
            .order_by(Product.last_seen.desc())
            .limit(50)  # Limit to prevent spam
            .all()
        )
        
        if not current_deals:
            return {
                "status": "success",
                "message": "No current deals available",
                "notifications_sent": 0
            }
        
        # Send notifications
        notifications_sent = await notification_service.send_new_deal_notifications(
            current_deals, db
        )
        
        return {
            "status": "success",
            "message": f"Manual notifications sent successfully",
            "notifications_sent": notifications_sent,
            "deals_processed": len(current_deals)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send manual notifications: {str(e)}"
        )