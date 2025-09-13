"""
Connection manager for WebSocket connections.
Handles connection lifecycle, session management, and cleanup.
"""
import asyncio
import logging
import time
import uuid
from typing import Any, Dict, Optional, Set

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and sessions."""

    def __init__(self):
        """Initialize connection manager."""
        # Connection storage
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.connection_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_connections: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_sessions": 0,
            "active_sessions": 0
        }
        
        logger.info("ConnectionManager initialized")

    async def add_connection(self, websocket: websockets.WebSocketServerProtocol, 
                           user: Optional[Any] = None) -> tuple[str, str]:
        """
        Add a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user: Optional user object
            
        Returns:
            Tuple of (connection_id, session_id)
        """
        try:
            # Generate IDs
            connection_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # Accept connection
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            
            # Create session info
            session_info = {
                "session_id": session_id,
                "user_id": user.id if user else None,
                "connected_at": time.time(),
                "last_activity": time.time(),
                "audio_chunks_received": 0,
                "transcriptions_sent": 0,
                "connection_count": 1
            }
            
            self.connection_sessions[connection_id] = session_info
            
            # Add to session connections
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
                self.stats["total_sessions"] += 1
                self.stats["active_sessions"] += 1
            else:
                # Increment connection count for existing session
                for existing_conn_id in self.session_connections[session_id]:
                    if existing_conn_id in self.connection_sessions:
                        self.connection_sessions[existing_conn_id]["connection_count"] += 1
                        break
            
            self.session_connections[session_id].add(connection_id)
            
            # Store connection metadata
            self.connection_metadata[connection_id] = {
                "user_agent": websocket.request_headers.get("User-Agent", "Unknown"),
                "remote_addr": websocket.remote_address,
                "connected_at": time.time()
            }
            
            # Update stats
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1
            
            logger.info(f"Connection added: {connection_id} for session {session_id}")
            
            return connection_id, session_id
            
        except Exception as e:
            logger.error(f"Error adding connection: {e}")
            raise

    async def remove_connection(self, connection_id: str) -> Optional[str]:
        """
        Remove a WebSocket connection.
        
        Args:
            connection_id: Connection ID to remove
            
        Returns:
            Session ID if connection was removed, None otherwise
        """
        try:
            if connection_id not in self.active_connections:
                logger.warning(f"Connection {connection_id} not found")
                return None
            
            # Get session ID
            session_id = self.connection_sessions.get(connection_id, {}).get("session_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            # Remove from connection sessions
            if connection_id in self.connection_sessions:
                del self.connection_sessions[connection_id]
            
            # Remove from session connections
            if session_id and session_id in self.session_connections:
                self.session_connections[session_id].discard(connection_id)
                
                # If no more connections in session, remove session
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
                    self.stats["active_sessions"] -= 1
            
            # Remove metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
            
            # Update stats
            self.stats["active_connections"] -= 1
            
            logger.info(f"Connection removed: {connection_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error removing connection: {e}")
            return None

    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
            
        Returns:
            True if message was sent successfully
        """
        try:
            if connection_id not in self.active_connections:
                logger.warning(f"Connection {connection_id} not found")
                return False
            
            websocket = self.active_connections[connection_id]
            await websocket.send(str(message))  # Convert to string for WebSocket
            
            # Update last activity
            if connection_id in self.connection_sessions:
                self.connection_sessions[connection_id]["last_activity"] = time.time()
            
            return True
            
        except ConnectionClosed:
            logger.info(f"Connection {connection_id} closed while sending message")
            await self.remove_connection(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]) -> int:
        """
        Broadcast message to all connections in a session.
        
        Args:
            session_id: Target session ID
            message: Message to broadcast
            
        Returns:
            Number of connections the message was sent to
        """
        sent_count = 0
        
        try:
            if session_id not in self.session_connections:
                logger.warning(f"Session {session_id} not found")
                return 0
            
            for connection_id in self.session_connections[session_id]:
                if await self.send_message(connection_id, message):
                    sent_count += 1
            
            logger.debug(f"Broadcasted message to {sent_count} connections in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting to session {session_id}: {e}")
        
        return sent_count

    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a connection.
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Connection information or None if not found
        """
        if connection_id not in self.connection_sessions:
            return None
        
        session_info = self.connection_sessions[connection_id].copy()
        metadata = self.connection_metadata.get(connection_id, {})
        
        return {
            **session_info,
            **metadata,
            "connection_id": connection_id
        }

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session information or None if not found
        """
        if session_id not in self.session_connections:
            return None
        
        connections = list(self.session_connections[session_id])
        connection_count = len(connections)
        
        # Get info from first connection (they should all have the same session info)
        first_connection_info = None
        if connections:
            first_connection_info = self.get_connection_info(connections[0])
        
        return {
            "session_id": session_id,
            "connection_count": connection_count,
            "connections": connections,
            "session_info": first_connection_info
        }

    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active connections."""
        return {
            conn_id: self.get_connection_info(conn_id)
            for conn_id in self.active_connections.keys()
        }

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sessions."""
        return {
            session_id: self.get_session_info(session_id)
            for session_id in self.session_connections.keys()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            **self.stats,
            "timestamp": time.time()
        }

    async def cleanup_inactive_connections(self, timeout: float = 300.0) -> int:
        """
        Clean up inactive connections.
        
        Args:
            timeout: Timeout in seconds for considering a connection inactive
            
        Returns:
            Number of connections cleaned up
        """
        current_time = time.time()
        cleaned_count = 0
        
        try:
            inactive_connections = []
            
            for connection_id, session_info in self.connection_sessions.items():
                last_activity = session_info.get("last_activity", session_info.get("connected_at", 0))
                if current_time - last_activity > timeout:
                    inactive_connections.append(connection_id)
            
            for connection_id in inactive_connections:
                await self.remove_connection(connection_id)
                cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} inactive connections")
            
        except Exception as e:
            logger.error(f"Error cleaning up inactive connections: {e}")
        
        return cleaned_count

    def is_connection_active(self, connection_id: str) -> bool:
        """
        Check if a connection is active.
        
        Args:
            connection_id: Connection ID to check
            
        Returns:
            True if connection is active
        """
        return connection_id in self.active_connections

    def get_connection_count(self) -> int:
        """Get current number of active connections."""
        return len(self.active_connections)

    def get_session_count(self) -> int:
        """Get current number of active sessions."""
        return len(self.session_connections)
