"""
Main FastAPI application entry point.

Configures middleware, routes, database, and background tasks.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis

from app.api.deps import get_current_user
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import engine
from app.db.base import Base
from app.services.websocket import manager
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Flashfood Tracker API...")

    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Initialize Redis connection
    try:
        app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        app.state.redis.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Continuing without cache.")
        app.state.redis = None

    yield

    # Shutdown
    logger.info("Shutting down Flashfood Tracker API...")
    if hasattr(app.state, "redis") and app.state.redis:
        app.state.redis.close()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Status and version information
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
    }


# WebSocket endpoint for real-time notifications
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
):
    """
    WebSocket endpoint for real-time deal notifications.

    Clients connect with JWT token for authentication.
    Receives real-time updates when new deals are found.

    Parameters:
        websocket: WebSocket connection
        token: JWT authentication token
    """
    # Note: In production, validate token properly
    # For now, we'll accept the connection
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")

            # Echo back for testing
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint with API information.

    Returns:
        Welcome message and documentation links
    """
    return {
        "message": "Flashfood Tracker API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
