"""
Email notification service using Resend.

Sends deal alerts and updates to users via email.
"""

import logging
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications.

    Uses Resend API for reliable email delivery.
    """

    def __init__(self):
        """Initialize email service with Resend API key."""
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM

        if not self.api_key:
            logger.warning("Resend API key not configured. Email notifications disabled.")

    async def send_new_deal_alert(
        self,
        to_email: str,
        user_name: str,
        deals: List[Dict[str, Any]],
    ) -> bool:
        """
        Send email alert about new deals.

        Parameters:
            to_email: Recipient email address
            user_name: User's display name
            deals: List of new deal dictionaries

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.api_key:
            logger.debug("Email sending skipped - no API key configured")
            return False

        try:
            import resend

            resend.api_key = self.api_key

            # Build email HTML
            deals_html = ""
            for deal in deals[:10]:  # Limit to 10 deals per email
                deals_html += f"""
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 8px 0;">{deal['name']}</h3>
                    <p style="margin: 0; color: #6b7280;">
                        <strong>${deal['discount_price']:.2f}</strong>
                        {f" (was ${deal['original_price']:.2f})" if deal.get('original_price') else ""}
                    </p>
                    <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">
                        {deal['store_name']} - {deal['store_city']}
                    </p>
                </div>
                """

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #10b981; margin-bottom: 20px;">New Flashfood Deals Available!</h1>

                <p>Hi {user_name},</p>

                <p>We found {len(deals)} new deals that match your preferences:</p>

                {deals_html}

                <p style="margin-top: 24px;">
                    <a href="http://localhost:5173" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        View All Deals
                    </a>
                </p>

                <p style="color: #6b7280; font-size: 14px; margin-top: 32px;">
                    You're receiving this email because you've enabled deal notifications in your Flashfood Tracker preferences.
                </p>
            </body>
            </html>
            """

            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": f"🆕 {len(deals)} New Flashfood Deals Available!",
                "html": html_content,
            }

            email = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}: {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_price_drop_alert(
        self,
        to_email: str,
        user_name: str,
        product_name: str,
        old_price: float,
        new_price: float,
        store_name: str,
    ) -> bool:
        """
        Send email alert about a price drop.

        Parameters:
            to_email: Recipient email address
            user_name: User's display name
            product_name: Name of the product
            old_price: Previous price
            new_price: New (lower) price
            store_name: Store where product is available

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.api_key:
            logger.debug("Email sending skipped - no API key configured")
            return False

        try:
            import resend

            resend.api_key = self.api_key

            savings = old_price - new_price
            savings_percent = int((savings / old_price) * 100)

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #ef4444; margin-bottom: 20px;">🔻 Price Drop Alert!</h1>

                <p>Hi {user_name},</p>

                <p>Great news! A product you're tracking has dropped in price:</p>

                <div style="border: 2px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0; background-color: #fef2f2;">
                    <h2 style="margin: 0 0 12px 0;">{product_name}</h2>
                    <p style="margin: 0; font-size: 24px; color: #ef4444;">
                        <strong>${new_price:.2f}</strong>
                        <span style="text-decoration: line-through; color: #6b7280; font-size: 18px; margin-left: 12px;">
                            ${old_price:.2f}
                        </span>
                    </p>
                    <p style="margin: 8px 0 0 0; color: #059669; font-weight: bold;">
                        Save ${savings:.2f} ({savings_percent}% off)
                    </p>
                    <p style="margin: 12px 0 0 0; color: #6b7280;">
                        Available at {store_name}
                    </p>
                </div>

                <p>
                    <a href="http://localhost:5173" style="background-color: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Claim This Deal
                    </a>
                </p>
            </body>
            </html>
            """

            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": f"🔻 Price Drop: {product_name} now ${new_price:.2f}!",
                "html": html_content,
            }

            email = resend.Emails.send(params)
            logger.info(f"Price drop email sent to {to_email}: {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send price drop email to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService()
