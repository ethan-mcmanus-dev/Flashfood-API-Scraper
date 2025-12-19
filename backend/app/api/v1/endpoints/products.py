"""
Product endpoints for listing deals and price history.
"""

from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.store import Store
from app.models.user import User
from app.schemas.product import ProductResponse, ProductWithStore, ProductWithHistory

router = APIRouter()


@router.get("/", response_model=List[ProductWithStore])
def list_products(
    city: Optional[str] = Query(None, description="Filter by city"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_discount: Optional[int] = Query(None, ge=0, le=100, description="Minimum discount percentage"),
    search: Optional[str] = Query(None, description="Search product names"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of products"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """
    List all available products (deals) with filtering options.

    Parameters:
        city: Filter by city
        store_id: Filter by specific store
        category: Filter by product category
        min_discount: Minimum discount percentage
        search: Search term for product names
        limit: Maximum results to return
        db: Database session
        current_user: Authenticated user

    Returns:
        List of products with store information
    """
    # Build query with store join
    query = db.query(Product).join(Store)

    # Apply filters
    if city:
        query = query.filter(Store.city == city)

    if store_id:
        query = query.filter(Product.store_id == store_id)

    if category:
        query = query.filter(Product.category == category)

    if min_discount is not None:
        query = query.filter(Product.discount_percent >= min_discount)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # Only show products still available (seen recently)
    query = query.filter(Product.quantity_available > 0)

    # Order by newest first
    query = query.order_by(Product.last_seen.desc())

    # Apply limit
    products = query.limit(limit).all()

    # Build response with store information
    result = []
    for product in products:
        result.append({
            "id": product.id,
            "store_id": product.store_id,
            "external_id": product.external_id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "original_price": product.original_price,
            "discount_price": product.discount_price,
            "discount_percent": product.discount_percent,
            "quantity_available": product.quantity_available,
            "expiry_date": product.expiry_date,
            "image_url": product.image_url,
            "first_seen": product.first_seen,
            "last_seen": product.last_seen,
            "store_name": product.store.name,
            "store_address": product.store.address,
            "store_city": product.store.city,
        })

    return result


@router.get("/{product_id}", response_model=ProductWithHistory)
def get_product_with_history(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get detailed product information including price history.

    Parameters:
        product_id: Product database ID
        db: Database session
        current_user: Authenticated user

    Returns:
        Product details with price history

    Raises:
        HTTPException: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Get price history
    price_history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.recorded_at.asc())
        .all()
    )

    return {
        "id": product.id,
        "store_id": product.store_id,
        "external_id": product.external_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "original_price": product.original_price,
        "discount_price": product.discount_price,
        "discount_percent": product.discount_percent,
        "quantity_available": product.quantity_available,
        "expiry_date": product.expiry_date,
        "image_url": product.image_url,
        "first_seen": product.first_seen,
        "last_seen": product.last_seen,
        "price_history": [
            {
                "price": ph.price,
                "quantity_available": ph.quantity_available,
                "recorded_at": ph.recorded_at,
            }
            for ph in price_history
        ],
    }


@router.get("/categories/list", response_model=List[str])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[str]:
    """
    Get list of all product categories.

    Parameters:
        db: Database session
        current_user: Authenticated user

    Returns:
        List of unique category names
    """
    categories = (
        db.query(Product.category)
        .filter(Product.category.isnot(None))
        .distinct()
        .all()
    )

    return [cat[0] for cat in categories if cat[0]]
