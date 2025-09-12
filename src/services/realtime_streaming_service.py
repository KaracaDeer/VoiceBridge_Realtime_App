"""
Real-time streaming service for VoiceBridge API
Handles WebSocket connections, audio streaming, and real-time text delivery
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Set

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from config import settings
from src.services.kafka_stream_service import kafka_stream_service
from src.services.model_monitoring_service import model_monitoring_service
from src.services.openai_whisper_service import get_openai_whisper_service
from src.services.prometheus_service import prometheus_metrics

logger = logging.getLogger(__name__)


class RealtimeStreamingService:
    """Service for real-time audio streaming and text delivery"""

    def __init__(self):
        self.whisper_service = get_openai_whisper_service(settings.openai_api_key)

        # Connection management
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.connection_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_connections: Dict[str, Set[str]] = {}

        # Audio streaming
        self.audio_buffers: Dict[str, List[bytes]] = {}
        self.buffer_lock = asyncio.Lock()

        # Text streaming
        self.text_subscribers: Dict[str, Set[str]] = {}
        self.text_queue: Dict[str, asyncio.Queue] = {}

        # Processing stats
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_audio_chunks": 0,
            "total_transcriptions": 0,
            "average_processing_time": 0.0,
        }

    async def handle_websocket_connection(self, websocket, path: str, user: Optional[Any] = None):
        """Handle new WebSocket connection"""
        connection_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        try:
            # Accept connection
            await websocket.accept()

            # Register connection
            self.active_connections[connection_id] = websocket
            self.connection_sessions[connection_id] = {
                "session_id": session_id,
                "user_id": user.id if user else None,
                "connected_at": time.time(),
                "audio_chunks_received": 0,
                "transcriptions_sent": 0,
                "last_activity": time.time(),
            }

            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(connection_id)

            # Initialize audio buffer
            async with self.buffer_lock:
                self.audio_buffers[session_id] = []

            # Initialize text queue
            self.text_queue[session_id] = asyncio.Queue()

            # Update stats
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1

            # Record metrics
            prometheus_metrics.record_websocket_connection(True)

            logger.info(f"WebSocket connection established: {connection_id} for session {session_id}")

            # Send welcome message
            await self._send_message(
                websocket,
                {
                    "type": "connection_established",
                    "connection_id": connection_id,
                    "session_id": session_id,
                    "timestamp": time.time(),
                },
            )

            # Start processing tasks
            processing_task = asyncio.create_task(self._process_audio_stream(session_id, connection_id))
            text_streaming_task = asyncio.create_task(self._stream_text_updates(session_id, websocket))

            # Handle incoming messages
            async for message in websocket:
                try:
                    await self._handle_websocket_message(websocket, message, connection_id, session_id)
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    try:
                        await self._send_error(websocket, f"Message processing error: {str(e)}")
                    except Exception:
                        pass  # Connection might be closed

        except ConnectionClosed:
            logger.info(f"WebSocket connection closed: {connection_id}")
        except WebSocketException as e:
            logger.error(f"WebSocket error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket connection: {e}")
        finally:
            # Cleanup
            await self._cleanup_connection(connection_id, session_id)

            # Cancel tasks
            if "processing_task" in locals() and processing_task:
                processing_task.cancel()
            if "text_streaming_task" in locals() and text_streaming_task:
                text_streaming_task.cancel()

    async def _handle_websocket_message(self, websocket, message, connection_id: str, session_id: str):
        """Handle incoming WebSocket message"""
        try:
            if isinstance(message, bytes):
                # Audio data
                await self._handle_audio_data(message, session_id, connection_id)
            elif isinstance(message, str):
                # Text message
                data = json.loads(message)
                await self._handle_text_message(websocket, data, connection_id, session_id)
        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_error(websocket, f"Message handling error: {str(e)}")

    async def _handle_audio_data(self, audio_data: bytes, session_id: str, connection_id: str):
        """Handle incoming audio data"""
        try:
            # Add to buffer
            async with self.buffer_lock:
                if session_id in self.audio_buffers:
                    self.audio_buffers[session_id].append(audio_data)

            # Update session info
            if connection_id in self.connection_sessions:
                self.connection_sessions[connection_id]["audio_chunks_received"] += 1
                self.connection_sessions[connection_id]["last_activity"] = time.time()

            # Update stats
            self.stats["total_audio_chunks"] += 1

            # Send acknowledgment
            websocket = self.active_connections.get(connection_id)
            if websocket:
                await self._send_message(
                    websocket,
                    {
                        "type": "audio_received",
                        "session_id": session_id,
                        "chunk_size": len(audio_data),
                        "timestamp": time.time(),
                    },
                )

            logger.debug(f"Received audio chunk for session {session_id}: {len(audio_data)} bytes")

        except Exception as e:
            logger.error(f"Error handling audio data: {e}")

    async def _handle_text_message(self, websocket, data: Dict[str, Any], connection_id: str, session_id: str):
        """Handle incoming text message"""
        try:
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping
                await self._send_message(websocket, {"type": "pong", "timestamp": time.time()})

            elif message_type == "get_status":
                # Send session status
                status = await self._get_session_status(session_id)
                await self._send_message(
                    websocket,
                    {
                        "type": "status",
                        "session_id": session_id,
                        "status": status,
                        "timestamp": time.time(),
                    },
                )

            elif message_type == "subscribe_text":
                # Subscribe to text updates
                if session_id not in self.text_subscribers:
                    self.text_subscribers[session_id] = set()
                self.text_subscribers[session_id].add(connection_id)

                await self._send_message(
                    websocket,
                    {
                        "type": "text_subscribed",
                        "session_id": session_id,
                        "timestamp": time.time(),
                    },
                )

            elif message_type == "unsubscribe_text":
                # Unsubscribe from text updates
                if session_id in self.text_subscribers:
                    self.text_subscribers[session_id].discard(connection_id)

                await self._send_message(
                    websocket,
                    {
                        "type": "text_unsubscribed",
                        "session_id": session_id,
                        "timestamp": time.time(),
                    },
                )

            else:
                await self._send_error(websocket, f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await self._send_error(websocket, f"Text message error: {str(e)}")

    async def _process_audio_stream(self, session_id: str, connection_id: str):
        """Process audio stream for a session"""
        logger.info(f"Started audio processing for session {session_id}")

        try:
            while connection_id in self.active_connections:
                # Check for audio data
                audio_chunks = []
                async with self.buffer_lock:
                    if session_id in self.audio_buffers and self.audio_buffers[session_id]:
                        audio_chunks = self.audio_buffers[session_id].copy()
                        self.audio_buffers[session_id].clear()

                if audio_chunks:
                    # Combine audio chunks
                    combined_audio = b"".join(audio_chunks)

                    # Process audio
                    start_time = time.time()
                    result = await self.whisper_service.transcribe_audio_bytes(
                        combined_audio, language=settings.default_language
                    )
                    processing_time = time.time() - start_time

                    # Record metrics
                    model_monitoring_service.record_model_performance(
                        model_name="whisper_realtime",
                        accuracy=result.get("confidence", 0.0),
                        confidence=result.get("confidence", 0.0),
                        processing_time=processing_time,
                        error_occurred="error" in result,
                    )

                    # Update stats
                    self.stats["total_transcriptions"] += 1
                    total_transcriptions = self.stats["total_transcriptions"]
                    if total_transcriptions > 0:
                        self.stats["average_processing_time"] = (
                            self.stats["average_processing_time"] * (total_transcriptions - 1) + processing_time
                        ) / total_transcriptions

                    # Send transcription result
                    if "error" not in result and result.get("text", "").strip():
                        await self._send_transcription_result(session_id, result, processing_time)

                    # Update session info
                    if connection_id in self.connection_sessions:
                        self.connection_sessions[connection_id]["transcriptions_sent"] += 1

                # Wait before next processing cycle
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info(f"Audio processing cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in audio processing for session {session_id}: {e}")

    async def _send_transcription_result(self, session_id: str, result: Dict[str, Any], processing_time: float):
        """Send transcription result to subscribers"""
        try:
            transcription_data = {
                "type": "transcription",
                "session_id": session_id,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", settings.default_language),
                "processing_time": processing_time,
                "timestamp": time.time(),
            }

            # Send to text queue
            if session_id in self.text_queue:
                await self.text_queue[session_id].put(transcription_data)

            # Send to Kafka for further processing
            if kafka_stream_service.producer:
                await kafka_stream_service.send_audio_chunk(
                    session_id=session_id,
                    user_id="realtime_user",  # Could be extracted from session
                    audio_data=b"",  # Empty for text-only result
                    language=result.get("language", settings.default_language),
                    is_final=True,
                )

            logger.debug(f"Sent transcription result for session {session_id}")

        except Exception as e:
            logger.error(f"Error sending transcription result: {e}")

    async def _stream_text_updates(self, session_id: str, websocket):
        """Stream text updates to WebSocket client"""
        try:
            while session_id in self.text_queue:
                try:
                    # Wait for text update
                    text_data = await asyncio.wait_for(self.text_queue[session_id].get(), timeout=1.0)

                    # Send to WebSocket
                    await self._send_message(websocket, text_data)

                except asyncio.TimeoutError:
                    # Send keepalive
                    await self._send_message(websocket, {"type": "keepalive", "timestamp": time.time()})
                except Exception as e:
                    logger.error(f"Error streaming text update: {e}")
                    break

        except asyncio.CancelledError:
            logger.info(f"Text streaming cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in text streaming for session {session_id}: {e}")

    async def _send_message(self, websocket, data: Dict[str, Any]):
        """Send message to WebSocket client"""
        try:
            await websocket.send(json.dumps(data))
        except ConnectionClosed:
            logger.debug("WebSocket connection closed while sending message")
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")

    async def _send_error(self, websocket, error_message: str):
        """Send error message to WebSocket client"""
        await self._send_message(
            websocket,
            {"type": "error", "message": error_message, "timestamp": time.time()},
        )

    async def _get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a session"""
        status = {
            "session_id": session_id,
            "active_connections": len(self.session_connections.get(session_id, set())),
            "audio_chunks_buffered": len(self.audio_buffers.get(session_id, [])),
            "text_subscribers": len(self.text_subscribers.get(session_id, set())),
            "timestamp": time.time(),
        }

        # Add connection-specific info
        for connection_id in self.session_connections.get(session_id, set()):
            if connection_id in self.connection_sessions:
                conn_info = self.connection_sessions[connection_id]
                status.update(
                    {
                        "audio_chunks_received": conn_info["audio_chunks_received"],
                        "transcriptions_sent": conn_info["transcriptions_sent"],
                        "connected_at": conn_info["connected_at"],
                        "last_activity": conn_info["last_activity"],
                    }
                )
                break

        return status

    async def _cleanup_connection(self, connection_id: str, session_id: str):
        """Clean up connection and session data"""
        try:
            # Remove from active connections
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

            # Remove from session connections
            if session_id in self.session_connections:
                self.session_connections[session_id].discard(connection_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]

            # Remove from connection sessions
            if connection_id in self.connection_sessions:
                del self.connection_sessions[connection_id]

            # Clean up audio buffer if no more connections
            if session_id not in self.session_connections:
                async with self.buffer_lock:
                    if session_id in self.audio_buffers:
                        del self.audio_buffers[session_id]

                # Clean up text queue
                if session_id in self.text_queue:
                    del self.text_queue[session_id]

                # Clean up text subscribers
                if session_id in self.text_subscribers:
                    del self.text_subscribers[session_id]

            # Update stats
            self.stats["active_connections"] = len(self.active_connections)

            # Record metrics
            prometheus_metrics.record_websocket_connection(False)

            logger.info(f"Cleaned up connection {connection_id} for session {session_id}")

        except Exception as e:
            logger.error(f"Error cleaning up connection: {e}")

    async def process_audio(self, audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process audio data and return transcription result"""
        try:
            audio_bytes = audio_data.get("audio_bytes", b"")
            if not audio_bytes:
                return {"error": "No audio data provided"}

            # Process audio with Whisper
            start_time = time.time()
            result = await self.whisper_service.transcribe_audio_bytes(audio_bytes, language=settings.default_language)
            processing_time = time.time() - start_time

            # Record metrics
            model_monitoring_service.record_model_performance(
                model_name="whisper_realtime",
                accuracy=result.get("confidence", 0.0),
                confidence=result.get("confidence", 0.0),
                processing_time=processing_time,
                error_occurred="error" in result,
            )

            # Update stats
            self.stats["total_transcriptions"] += 1
            total_transcriptions = self.stats["total_transcriptions"]
            if total_transcriptions > 0:
                self.stats["average_processing_time"] = (
                    self.stats["average_processing_time"] * (total_transcriptions - 1) + processing_time
                ) / total_transcriptions

            return {
                "success": True,
                "transcription": result.get("text", ""),
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", settings.default_language),
                "processing_time": processing_time,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self.stats,
            "active_sessions": len(self.session_connections),
            "total_text_subscribers": sum(len(subs) for subs in self.text_subscribers.values()),
            "timestamp": time.time(),
        }

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """Broadcast message to all connections in a session"""
        try:
            if session_id in self.session_connections:
                for connection_id in self.session_connections[session_id]:
                    if connection_id in self.active_connections:
                        websocket = self.active_connections[connection_id]
                        await self._send_message(websocket, message)
        except Exception as e:
            logger.error(f"Error broadcasting to session {session_id}: {e}")


# Global real-time streaming service instance
realtime_streaming_service = RealtimeStreamingService()
