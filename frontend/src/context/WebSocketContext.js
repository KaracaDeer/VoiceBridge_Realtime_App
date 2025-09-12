/**
 * WebSocket Context for Real-time Communication
 * 
 * This context provides WebSocket connection management for real-time audio streaming
 * between the frontend and backend. It handles:
 * - Connection establishment and management
 * - Automatic reconnection on connection loss
 * - Audio data transmission
 * - Message handling and state management
 */

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000;

  const connect = () => {
    try {
      // Get WebSocket URL from environment or use default localhost
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
      // Generate unique client ID for this session
      const clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const newSocket = new WebSocket(`${wsUrl}/ws/${clientId}`);

      newSocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        setSocket(newSocket);
        reconnectAttemptsRef.current = 0;
      };

      newSocket.onmessage = (event) => {
        setLastMessage(event.data);
        console.log('WebSocket message received:', event.data);
      };

      newSocket.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        setSocket(null);
        
        if (event.code !== 1000) { // Not a normal closure
          attemptReconnect();
        }
      };

      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setConnectionStatus('error');
    }
  };

  const attemptReconnect = () => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      setConnectionStatus('failed');
      return;
    }

    reconnectAttemptsRef.current += 1;
    setConnectionStatus('reconnecting');
    
    console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, reconnectDelay * reconnectAttemptsRef.current);
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (socket) {
      socket.close(1000, 'User disconnected');
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
    setSocket(null);
  };

  const sendAudio = (audioData) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        socket.send(audioData);
        console.log('Audio data sent to server');
        return true;
      } catch (error) {
        console.error('Error sending audio data:', error);
        return false;
      }
    } else {
      console.warn('WebSocket not connected');
      return false;
    }
  };

  const sendMessage = (message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        socket.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Error sending message:', error);
        return false;
      }
    }
    return false;
  };

  useEffect(() => {
    // Auto-connect on mount
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, []);

  const value = {
    socket,
    isConnected,
    connectionStatus,
    lastMessage,
    connect,
    disconnect,
    sendAudio,
    sendMessage,
    reconnectAttempts: reconnectAttemptsRef.current,
    maxReconnectAttempts
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
