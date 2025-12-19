"""
Store endpoints for listing and filtering stores.
"""

from typing import List, Optional
from math import radians, cos, sin, asin, sqrt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.store import Store
from app.models.user import User
from app.schemas.store import StoreResponse, StoreWithDistance

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Uses the Haversine formula for accuracy.

    Parameters:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate

    Returns:
        Distance in kilometers
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Radius of Earth in kilometers
    r = 6371

    return c * r


@router.get("/", response_model=List[StoreWithDistance])
def list_stores(
    city: Optional[str] = Query(None, description="Filter by city (calgary, vancouver, etc.)"),
    max_distance_km: Optional[float] = Query(None, ge=1, le=200, description="Maximum distance from city center"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """
    List all stores with distance calculations.

    Filters by city and distance from city center.

    Parameters:
        city: Optional city filter
        max_distance_km: Optional maximum distance filter
        db: Database session
        current_user: Authenticated user

    Returns:
        List of stores with calculated distances
    """
    # Build query
    query = db.query(Store)

    # Apply city filter
    if city:
        query = query.filter(Store.city == city)

    stores = query.all()

    # Get city coordinates for distance calculation
    city_coords = None
    if city and city in settings.SUPPORTED_CITIES:
        city_info = settings.SUPPORTED_CITIES[city]
        city_coords = (city_info["lat"], city_info["lon"])

    # Calculate distances and filter
    result = []
    for store in stores:
        store_dict = {
            "id": store.id,
            "external_id": store.external_id,
            "name": store.name,
            "address": store.address,
            "city": store.city,
            "latitude": store.latitude,
            "longitude": store.longitude,
            "created_at": store.created_at,
            "updated_at": store.updated_at,
        }

        # Calculate distance from city center
        if city_coords:
            distance = calculate_distance(
                city_coords[0],
                city_coords[1],
                store.latitude,
                store.longitude,
            )
            store_dict["distance_km"] = round(distance, 2)

            # Apply distance filter
            if max_distance_km and distance > max_distance_km:
                continue
        else:
            store_dict["distance_km"] = 0.0

        result.append(store_dict)

    # Sort by distance
    result.sort(key=lambda x: x["distance_km"])

    return result


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Store:
    """
    Get detailed information for a specific store.

    Parameters:
        store_id: Store database ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Store details

    Raises:
        HTTPException: If store not found
    """
    from fastapi import HTTPException, status

    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found",
        )

    return store
