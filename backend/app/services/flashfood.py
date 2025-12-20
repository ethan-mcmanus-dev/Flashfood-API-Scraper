"""
Flashfood API integration service.

Handles communication with the reverse-engineered Flashfood mobile API.
Implements rate limiting, caching, and error handling.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging

import httpx
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class FlashfoodAPIError(Exception):
    """Custom exception for Flashfood API errors."""

    pass


class FlashfoodService:
    """
    Service for interacting with the Flashfood API.

    This service reverse-engineers the mobile app's REST API to fetch
    store and product information programmatically.
    """

    def __init__(self, redis_client: Optional[Redis] = None):
        """
        Initialize Flashfood service.

        Parameters:
            redis_client: Optional Redis client for caching responses
        """
        self.base_url = settings.FLASHFOOD_BASE_URL
        self.api_key = settings.FLASHFOOD_API_KEY
        self.redis_client = redis_client
        self.cache_ttl = 300  # Cache for 5 minutes

        # Headers mimicking iOS mobile app
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CA",
            "Connection": "keep-alive",
            "flashfood-app-info": "app/shopper,appversion/3.2.6,appbuild/35155,os/ios,osversion/18.6.1,devicemodel/Apple_iPhone14_5,deviceid/unknown",
            "User-Agent": "Flashfood/35155 CFNetwork/3826.600.41 Darwin/24.6.0",
            "x-ff-api-key": self.api_key,
        }

    async def get_stores_near_location(
        self,
        latitude: float,
        longitude: float,
        max_distance_meters: int = 75000,
        limit: int = 50,
        include_items: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch stores near a geographic location.

        Parameters:
            latitude: Search center latitude
            longitude: Search center longitude
            max_distance_meters: Maximum search radius in meters (default 75km)
            limit: Maximum number of stores to return
            include_items: Include item listings in response

        Returns:
            Dictionary containing store data from Flashfood API

        Raises:
            FlashfoodAPIError: If API request fails
        """
        # Check cache first
        cache_key = f"stores:{latitude}:{longitude}:{max_distance_meters}:{limit}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for stores near {latitude},{longitude}")
                import json
                return json.loads(cached)

        # Build request URL
        url = f"{self.base_url}/stores"
        params = {
            "storesWithItemsLimit": limit,
            "includeItems": str(include_items).lower(),
            "searchLatitude": latitude,
            "searchLongitude": longitude,
            "userLocationLatitude": latitude,
            "userLocationLongitude": longitude,
            "maxDistance": max_distance_meters,
        }

        # Make request
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                # Cache successful response
                if self.redis_client:
                    import json
                    self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

                logger.info(f"Fetched {len(data.get('data', {}))} stores near {latitude},{longitude}")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching stores: {e.response.status_code}")
            raise FlashfoodAPIError(f"API returned status {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching stores: {str(e)}")
            raise FlashfoodAPIError(f"Failed to connect to Flashfood API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching stores: {str(e)}")
            raise FlashfoodAPIError(f"Unexpected error: {str(e)}")

    async def get_items_for_store(self, store_id: str) -> Dict[str, Any]:
        """
        Fetch all items available at a specific store.

        Parameters:
            store_id: Flashfood store identifier

        Returns:
            Dictionary containing item data for the store

        Raises:
            FlashfoodAPIError: If API request fails
        """
        # Check cache first
        cache_key = f"items:{store_id}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for store {store_id} items")
                import json
                return json.loads(cached)

        # Build request URL
        url = f"{self.base_url}/items/"
        params = {"storeIds": store_id}

        # Make request
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                # Cache successful response
                if self.redis_client:
                    import json
                    self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(data))

                items = data.get("data", {}).get(store_id, [])
                logger.info(f"Fetched {len(items)} items for store {store_id}")
                return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching items for store {store_id}: {e.response.status_code}")
            raise FlashfoodAPIError(f"API returned status {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching items: {str(e)}")
            raise FlashfoodAPIError(f"Failed to connect to Flashfood API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching items: {str(e)}")
            raise FlashfoodAPIError(f"Unexpected error: {str(e)}")

    def parse_store_data(self, raw_store: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw Flashfood store data into normalized format.

        Parameters:
            raw_store: Raw store data from Flashfood API

        Returns:
            Normalized store dictionary
        """
        return {
            "external_id": raw_store.get("id"),
            "name": raw_store.get("name", "Unknown Store"),
            "address": raw_store.get("address", {}).get("fullAddress"),
            "latitude": raw_store.get("location", {}).get("latitude"),
            "longitude": raw_store.get("location", {}).get("longitude"),
        }

    def parse_item_data(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw Flashfood item data into normalized format.

        Parameters:
            raw_item: Raw item data from Flashfood API

        Returns:
            Normalized product dictionary
        """
        # Helper function to safely convert price to float
        def safe_price_convert(price_value):
            """Convert price to float, handling both strings and numbers."""
            if price_value is None:
                return 0.0
            try:
                return float(price_value)
            except (ValueError, TypeError):
                return 0.0

        # Calculate discount percentage with safe type conversion
        original_price_raw = raw_item.get("originalPrice")
        discount_price_raw = raw_item.get("price", 0)
        
        original_price = safe_price_convert(original_price_raw)
        discount_price = safe_price_convert(discount_price_raw)
        discount_percent = None

        if original_price and original_price > 0:
            discount_percent = int(((original_price - discount_price) / original_price) * 100)

        # Parse expiry date
        expiry_date = None
        if raw_item.get("expiryDate"):
            try:
                expiry_date = datetime.fromisoformat(raw_item["expiryDate"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return {
            "external_id": raw_item.get("id"),
            "name": raw_item.get("name", "Unknown Item"),
            "description": raw_item.get("description"),
            "category": raw_item.get("category"),
            "original_price": original_price,
            "discount_price": discount_price,
            "discount_percent": discount_percent,
            "quantity_available": raw_item.get("quantityAvailable", 0),
            "expiry_date": expiry_date,
            "image_url": raw_item.get("image", {}).get("url") if raw_item.get("image") else None,
        }
