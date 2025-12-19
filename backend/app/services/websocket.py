"""
WebSocket connection manager for real-time notifications.

Manages WebSocket connections and broadcasts deal updates to connected clients.
"""

from typing import Dict, Set
import logging
import json

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and message broadcasting.

    Maintains a set of active connections and provides methods to
    send messages to all or specific clients.
    """

    def __init__(self):
        """Initialize connection manager with empty connection set."""
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int | None = None):
        """
        Accept new WebSocket connection.

        Parameters:
            websocket: WebSocket instance to connect
            user_id: Optional user ID for targeted messaging
        """
        await websocket.accept()
        self.active_connections.add(websocket)

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)

        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: int | None = None):
        """
        Remove WebSocket connection.

        Parameters:
            websocket: WebSocket instance to disconnect
            user_id: Optional user ID to remove from user connections
        """
        self.active_connections.discard(websocket)

        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.

        Parameters:
            message: Dictionary to send as JSON
        """
        if not self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def send_to_user(self, user_id: int, message: dict):
        """
        Send message to specific user's connections.

        Parameters:
            user_id: Target user ID
            message: Dictionary to send as JSON
        """
        if user_id not in self.user_connections:
            return

        message_json = json.dumps(message)
        disconnected = set()

        for connection in self.user_connections[user_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, user_id)


# Global connection manager instance
manager = ConnectionManager()
