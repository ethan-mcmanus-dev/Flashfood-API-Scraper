"""
Background task scheduler for polling Flashfood API.

Periodically fetches new deals and sends notifications to users.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Set, Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.store import Store
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.user import User
from app.models.user_preference import UserPreference
from app.services.flashfood import FlashfoodService
from app.services.websocket import manager
from app.services.notification import notification_service

logger = logging.getLogger(__name__)


class FlashfoodScheduler:
    """
    Background scheduler for monitoring Flashfood deals.

    Polls Flashfood API at regular intervals, detects new deals,
    and broadcasts notifications to connected clients.
    """

    def __init__(self, redis_client: Redis | None = None):
        """
        Initialize scheduler.

        Parameters:
            redis_client: Optional Redis client for caching
        """
        self.scheduler = AsyncIOScheduler()
        self.flashfood_service = FlashfoodService(redis_client)
        self.tracked_cities = settings.SUPPORTED_CITIES
        self.is_running = False

    async def fetch_and_update_deals(self):
        """
        Main polling task that fetches deals for all tracked cities.

        Updates database with new deals and broadcasts notifications.
        """
        logger.info("Starting Flashfood deal refresh cycle...")
        db = SessionLocal()

        try:
            new_deals_count = 0
            new_deals_list = []  # Track new deals for notifications

            # Iterate through each tracked city
            for city_key, city_info in self.tracked_cities.items():
                logger.info(f"Fetching deals for {city_info['name']}...")

                try:
                    # Fetch stores with items from Flashfood API
                    response = await self.flashfood_service.get_stores_near_location(
                        latitude=city_info["lat"],
                        longitude=city_info["lon"],
                        max_distance_meters=75000,
                        limit=50,
                        include_items=True,
                    )

                    # Process stores and items
                    stores_data = response.get("data", [])

                    for store_data in stores_data:
                        # Parse and upsert store
                        store_info = self.flashfood_service.parse_store_data(store_data)
                        store_info["city"] = city_key

                        db_store = db.query(Store).filter(
                            Store.external_id == store_info["external_id"]
                        ).first()

                        if not db_store:
                            db_store = Store(**store_info)
                            db.add(db_store)
                            db.commit()
                            db.refresh(db_store)
                            logger.info(f"Added new store: {store_info['name']}")
                        else:
                            # Update existing store
                            for key, value in store_info.items():
                                setattr(db_store, key, value)
                            db.commit()

                        # Process items for this store
                        items = store_data.get("items", [])
                        new_items, new_products = await self._process_store_items(db, db_store, items)
                        new_deals_count += new_items
                        new_deals_list.extend(new_products)  # Add new products to notification list

                except Exception as e:
                    logger.error(f"Error fetching deals for {city_info['name']}: {e}")
                    continue

            logger.info(f"Deal refresh complete. Found {new_deals_count} new deals.")

            # Send email notifications for new deals
            if new_deals_list:
                try:
                    notifications_sent = await notification_service.send_new_deal_notifications(new_deals_list, db)
                    logger.info(f"Sent {notifications_sent} email notifications")
                except Exception as e:
                    logger.error(f"Error sending notifications: {e}")

            # Broadcast WebSocket notification if new deals found
            if new_deals_count > 0:
                await manager.broadcast({
                    "type": "new_deals",
                    "count": new_deals_count,
                    "message": f"{new_deals_count} new deals available!",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        except Exception as e:
            logger.error(f"Error in deal refresh cycle: {e}")
        finally:
            db.close()

    async def _process_store_items(
        self,
        db: Session,
        store: Store,
        items: list[Dict[str, Any]],
    ) -> tuple[int, list[Product]]:
        """
        Process items for a store and detect new deals.

        Parameters:
            db: Database session
            store: Store model instance
            items: List of raw item data from Flashfood API

        Returns:
            Tuple of (number of new items detected, list of new Product objects)
        """
        new_items_count = 0
        new_products = []
        current_external_ids = set()

        for item_data in items:
            try:
                # Parse item data
                item_info = self.flashfood_service.parse_item_data(item_data)
                item_info["store_id"] = store.id
                current_external_ids.add(item_info["external_id"])

                # Check if product already exists
                db_product = db.query(Product).filter(
                    Product.store_id == store.id,
                    Product.external_id == item_info["external_id"],
                ).first()

                if not db_product:
                    # New product detected!
                    db_product = Product(**item_info)
                    db.add(db_product)
                    db.commit()
                    db.refresh(db_product)

                    # Load the store relationship for notifications
                    db_product.store = store

                    logger.info(f"New deal: {item_info['name']} at {store.name} for ${item_info['discount_price']}")
                    new_items_count += 1
                    new_products.append(db_product)  # Add to notification list

                    # Record initial price history
                    price_history = PriceHistory(
                        product_id=db_product.id,
                        price=item_info["discount_price"],
                        quantity_available=item_info["quantity_available"],
                    )
                    db.add(price_history)
                else:
                    # Update existing product
                    price_changed = db_product.discount_price != item_info["discount_price"]
                    quantity_changed = db_product.quantity_available != item_info["quantity_available"]

                    for key, value in item_info.items():
                        if key != "store_id":  # Don't update store_id
                            setattr(db_product, key, value)

                    db_product.last_seen = datetime.now(timezone.utc)

                    # Record price history if price or quantity changed
                    if price_changed or quantity_changed:
                        price_history = PriceHistory(
                            product_id=db_product.id,
                            price=item_info["discount_price"],
                            quantity_available=item_info["quantity_available"],
                        )
                        db.add(price_history)

                db.commit()

            except Exception as e:
                logger.error(f"Error processing item {item_data.get('name', 'unknown')}: {e}")
                continue

        # Mark products as out of stock if they're no longer in the API response
        # (quantity_available = 0 for products not seen in this refresh)
        stale_products = db.query(Product).filter(
            Product.store_id == store.id,
            Product.external_id.notin_(current_external_ids),
            Product.quantity_available > 0,
        ).all()

        for product in stale_products:
            product.quantity_available = 0
            product.last_seen = datetime.now(timezone.utc)
            logger.debug(f"Marked product as out of stock: {product.name}")

        db.commit()

        return new_items_count, new_products

    def start(self):
        """Start the background scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Schedule the polling task
        self.scheduler.add_job(
            self.fetch_and_update_deals,
            "interval",
            seconds=settings.FLASHFOOD_POLL_INTERVAL_SECONDS,
            id="flashfood_polling",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True
        logger.info(f"Scheduler started. Polling every {settings.FLASHFOOD_POLL_INTERVAL_SECONDS} seconds.")

    def stop(self):
        """Stop the background scheduler."""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped.")


# Global scheduler instance
scheduler = FlashfoodScheduler()
