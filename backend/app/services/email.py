"""
Email notification service supporting multiple providers.

Supports Gmail SMTP (free), Resend API, and other providers.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications via multiple providers.
    
    Supports Gmail SMTP (free, no domain required) and Resend API.
    """

    def __init__(self):
        """Initialize email service based on configuration."""
        self.service = settings.EMAIL_SERVICE
        
        if self.service == "gmail":
            self.gmail_email = settings.GMAIL_EMAIL
            self.gmail_password = settings.GMAIL_APP_PASSWORD
            
            if not self.gmail_email or not self.gmail_password:
                logger.warning("Gmail credentials not configured. Using mock email service for testing.")
                self.service = "mock"
            else:
                logger.info(f"Gmail SMTP configured for {self.gmail_email}")
                
        elif self.service == "resend":
            self.api_key = settings.RESEND_API_KEY
            self.from_email = settings.EMAIL_FROM
            
            if not self.api_key:
                logger.warning("Resend API key not configured. Using mock email service for testing.")
                self.service = "mock"
            else:
                logger.info(f"Resend API key configured: {self.api_key[:10]}...{self.api_key[-4:]} (length: {len(self.api_key)})")
        else:
            logger.warning("No email service configured. Using mock email service for testing.")
            self.service = "mock"

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
        if self.service == "mock":
            logger.info(f"MOCK EMAIL - Would send to {to_email}:")
            logger.info(f"Subject: 🆕 {len(deals)} New Flashfood Deals Available!")
            logger.info(f"Recipient: {user_name} ({to_email})")
            logger.info(f"Deals: {[deal['name'] for deal in deals[:5]]}")
            return True

        elif self.service == "gmail":
            return await self._send_via_gmail(to_email, user_name, deals)
            
        elif self.service == "resend":
            return await self._send_via_resend(to_email, user_name, deals)
            
        return False

    async def _send_via_gmail(
        self,
        to_email: str,
        user_name: str,
        deals: List[Dict[str, Any]],
    ) -> bool:
        """Send email via Gmail SMTP."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🆕 {len(deals)} New Flashfood Deals Available!"
            msg['From'] = self.gmail_email
            msg['To'] = to_email

            # Create HTML content
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

                <p style="color: #6b7280; font-size: 14px; margin-top: 32px;">
                    You're receiving this email because you've enabled deal notifications in your Flashfood Tracker preferences.
                </p>
            </body>
            </html>
            """

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.gmail_email, self.gmail_password)
                server.send_message(msg)

            logger.info(f"Gmail email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Gmail email to {to_email}: {e}")
            return False

    async def _send_via_resend(
        self,
        to_email: str,
        user_name: str,
        deals: List[Dict[str, Any]],
    ) -> bool:
        """Send email via Resend API."""
        try:
            import resend

            resend.api_key = self.api_key

            # Build email HTML (same as Gmail)
            deals_html = ""
            for deal in deals[:10]:
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
            logger.info(f"Resend email sent successfully to {to_email}: {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send Resend email to {to_email}: {e}")
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
        """
        if self.service == "mock":
            logger.info(f"MOCK EMAIL - Would send price drop alert to {to_email}:")
            logger.info(f"Subject: 🔻 Price Drop: {product_name} now ${new_price:.2f}!")
            logger.info(f"Recipient: {user_name} ({to_email})")
            logger.info(f"Product: {product_name} at {store_name}")
            logger.info(f"Price: ${old_price:.2f} → ${new_price:.2f}")
            return True

        # Implementation for Gmail and Resend would be similar to send_new_deal_alert
        # For now, just use the mock implementation
        return True


# Global email service instance
email_service = EmailService()