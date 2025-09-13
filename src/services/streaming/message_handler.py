"""
Message handler for WebSocket communication.
Handles different message types and routing.
"""
import json
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles WebSocket messages and routing."""

    def __init__(self):
        """Initialize message handler."""
        self.message_handlers: Dict[str, callable] = {}
        self.message_stats = {
            "total_messages": 0,
            "messages_by_type": {},
            "errors": 0,
            "last_message_time": 0
        }
        
        # Register default handlers
        self._register_default_handlers()
        
        logger.info("MessageHandler initialized")

    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("get_status", self._handle_get_status)
        self.register_handler("subscribe_text", self._handle_subscribe_text)
        self.register_handler("unsubscribe_text", self._handle_unsubscribe_text)
        self.register_handler("audio_chunk", self._handle_audio_chunk)
        self.register_handler("transcription_request", self._handle_transcription_request)

    def register_handler(self, message_type: str, handler: callable):
        """
        Register a message handler.
        
        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")

    async def handle_message(self, websocket, message: str, 
                           connection_id: str, session_id: str,
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: WebSocket connection
            message: Message content
            connection_id: Connection ID
            session_id: Session ID
            context: Additional context
            
        Returns:
            Handler result
        """
        try:
            # Parse message
            if isinstance(message, str):
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    return await self._handle_error(websocket, "Invalid JSON message")
            else:
                # Handle binary messages (audio data)
                return await self._handle_binary_message(websocket, message, connection_id, session_id, context)
            
            # Get message type
            message_type = data.get("type", "unknown")
            
            # Update stats
            self.message_stats["total_messages"] += 1
            self.message_stats["messages_by_type"][message_type] = (
                self.message_stats["messages_by_type"].get(message_type, 0) + 1
            )
            self.message_stats["last_message_time"] = time.time()
            
            # Find handler
            handler = self.message_handlers.get(message_type)
            if not handler:
                return await self._handle_error(websocket, f"Unknown message type: {message_type}")
            
            # Call handler
            result = await handler(websocket, data, connection_id, session_id, context)
            
            logger.debug(f"Handled message type {message_type} for connection {connection_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.message_stats["errors"] += 1
            return await self._handle_error(websocket, f"Message handling error: {str(e)}")

    async def _handle_binary_message(self, websocket, message: bytes, 
                                   connection_id: str, session_id: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle binary message (audio data).
        
        Args:
            websocket: WebSocket connection
            message: Binary message content
            connection_id: Connection ID
            session_id: Session ID
            context: Additional context
            
        Returns:
            Handler result
        """
        try:
            # Create audio chunk message
            audio_message = {
                "type": "audio_chunk",
                "data": message,
                "size": len(message),
                "timestamp": time.time()
            }
            
            # Handle as audio chunk
            return await self._handle_audio_chunk(websocket, audio_message, connection_id, session_id, context)
            
        except Exception as e:
            logger.error(f"Error handling binary message: {e}")
            return await self._handle_error(websocket, f"Binary message error: {str(e)}")

    async def _handle_ping(self, websocket, data: Dict[str, Any], 
                         connection_id: str, session_id: str,
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle ping message."""
        try:
            response = {
                "type": "pong",
                "timestamp": time.time(),
                "connection_id": connection_id,
                "session_id": session_id
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling ping: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_get_status(self, websocket, data: Dict[str, Any], 
                               connection_id: str, session_id: str,
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle status request message."""
        try:
            # Get status from context if available
            status = context.get("status", {}) if context else {}
            
            response = {
                "type": "status",
                "connection_id": connection_id,
                "session_id": session_id,
                "status": status,
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling get_status: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_subscribe_text(self, websocket, data: Dict[str, Any], 
                                   connection_id: str, session_id: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle text subscription message."""
        try:
            # Add to text subscribers if context available
            if context and "text_subscribers" in context:
                if session_id not in context["text_subscribers"]:
                    context["text_subscribers"][session_id] = set()
                context["text_subscribers"][session_id].add(connection_id)
            
            response = {
                "type": "text_subscribed",
                "connection_id": connection_id,
                "session_id": session_id,
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling subscribe_text: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_unsubscribe_text(self, websocket, data: Dict[str, Any], 
                                     connection_id: str, session_id: str,
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle text unsubscription message."""
        try:
            # Remove from text subscribers if context available
            if context and "text_subscribers" in context:
                if session_id in context["text_subscribers"]:
                    context["text_subscribers"][session_id].discard(connection_id)
            
            response = {
                "type": "text_unsubscribed",
                "connection_id": connection_id,
                "session_id": session_id,
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling unsubscribe_text: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_audio_chunk(self, websocket, data: Dict[str, Any], 
                                connection_id: str, session_id: str,
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle audio chunk message."""
        try:
            # Process audio chunk if context available
            if context and "audio_processor" in context:
                audio_data = data.get("data", b"")
                if audio_data:
                    await context["audio_processor"].add_audio_chunk(session_id, audio_data)
            
            response = {
                "type": "audio_received",
                "connection_id": connection_id,
                "session_id": session_id,
                "chunk_size": data.get("size", 0),
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling audio_chunk: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_transcription_request(self, websocket, data: Dict[str, Any], 
                                          connection_id: str, session_id: str,
                                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle transcription request message."""
        try:
            # Process transcription request if context available
            if context and "transcription_pipeline" in context:
                # This would trigger transcription processing
                pass
            
            response = {
                "type": "transcription_requested",
                "connection_id": connection_id,
                "session_id": session_id,
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(response))
            return {"success": True, "response": response}
            
        except Exception as e:
            logger.error(f"Error handling transcription_request: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_error(self, websocket, error_message: str) -> Dict[str, Any]:
        """Handle error and send error response."""
        try:
            error_response = {
                "type": "error",
                "message": error_message,
                "timestamp": time.time()
            }
            
            await websocket.send(json.dumps(error_response))
            return {"success": False, "error": error_message}
            
        except Exception as e:
            logger.error(f"Error sending error response: {e}")
            return {"success": False, "error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Get message handler statistics."""
        return {
            **self.message_stats,
            "registered_handlers": list(self.message_handlers.keys()),
            "timestamp": time.time()
        }

    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about registered handlers."""
        return {
            "total_handlers": len(self.message_handlers),
            "handlers": list(self.message_handlers.keys()),
            "stats": self.get_stats()
        }
