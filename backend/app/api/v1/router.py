"""
API v1 router that combines all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, stores, products, preferences, notifications

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
