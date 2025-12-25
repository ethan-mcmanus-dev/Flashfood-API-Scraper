/**
 * WebSocket hook for real-time deal notifications.
 *
 * Manages WebSocket connection lifecycle and message handling.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { WebSocketMessage } from '../types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: string) => void;
  reconnect: () => void;
}

/**
 * Hook for managing WebSocket connection to receive real-time updates.
 *
 * @param token - Authentication token for WebSocket connection
 * @param options - Event handlers for connection lifecycle
 * @returns WebSocket connection state and methods
 */
export const useWebSocket = (
  token: string | null,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const { onMessage, onConnect, onDisconnect, onError } = options;

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  /**
   * Connect to WebSocket server.
   */
  const connect = useCallback(() => {
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(`${WS_URL}?token=${token}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        onConnect?.();
      };

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        onDisconnect?.();

        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          connect();
        }, 5000);
      };

      ws.onerror = (error: Event) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [token, onMessage, onConnect, onDisconnect, onError]);

  /**
   * Send message through WebSocket.
   */
  const sendMessage = useCallback((message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message);
    } else {
      console.warn('WebSocket is not connected. Cannot send message.');
    }
  }, []);

  /**
   * Manually trigger reconnection.
   */
  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    connect();
  }, [connect]);

  /**
   * Connect on mount and disconnect on unmount.
   */
  useEffect(() => {
    if (token) {
      connect();
    }

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token, connect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnect,
  };
};
