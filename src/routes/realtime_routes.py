"""
Real-time Streaming Routes for VoiceBridge API

This module handles real-time audio streaming and transcription endpoints:

- WebSocket connections for live audio streaming
- Real-time transcription processing
- gRPC endpoints for high-performance communication
- Streaming status monitoring and health checks
- Authentication and session management for streaming

Key endpoints:
- /ws/stream - WebSocket for real-time audio streaming
- /grpc/stream - gRPC streaming endpoint
- /status - Streaming service status
"""
import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status

# from src.database.mysql_models import User  # Temporarily disabled
from src.services.auth_service import get_current_user
from src.services.grpc_service import grpc_server
from src.services.kafka_stream_service import kafka_stream_service
from src.services.realtime_streaming_service import realtime_streaming_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/realtime", tags=["realtime-streaming"])


@router.websocket("/ws/stream")
async def websocket_audio_stream(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time audio streaming and transcription.

    This endpoint handles:
    - Real-time audio data reception from frontend
    - Audio processing and transcription
    - Live transcription results streaming back to client
    - Connection management and error handling
    """
    user = None

    # Optional authentication
    if token:
        try:
            from src.services.auth_service import auth_service

            payload = auth_service.verify_token(token, "access")
            user_id = int(payload.get("sub"))
            user = auth_service.get_user_by_id(user_id)
        except Exception as e:
            logger.warning(f"Invalid token for WebSocket connection: {e}")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return

    # Handle WebSocket connection
    await realtime_streaming_service.handle_websocket_connection(websocket, "/realtime/ws/stream", user)


@router.websocket("/ws/stream/{session_id}")
async def websocket_audio_stream_with_session(
    websocket: WebSocket, session_id: str, token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time audio streaming with specific session ID
    """
    user = None

    # Optional authentication
    if token:
        try:
            from src.services.auth_service import auth_service

            payload = auth_service.verify_token(token, "access")
            user_id = int(payload.get("sub"))
            user = auth_service.get_user_by_id(user_id)
        except Exception as e:
            logger.warning(f"Invalid token for WebSocket connection: {e}")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return

    # Handle WebSocket connection
    await realtime_streaming_service.handle_websocket_connection(websocket, f"/realtime/ws/stream/{session_id}", user)


@router.get("/status")
async def get_realtime_status():
    """Get real-time streaming service status"""
    try:
        stats = await realtime_streaming_service.get_service_stats()
        kafka_stats = await kafka_stream_service.get_processing_stats()

        return {
            "status": "active",
            "websocket_service": stats,
            "kafka_service": kafka_stats,
            "grpc_service": {
                "status": "active" if grpc_server.server else "inactive",
                "port": 50051,
            },
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error getting real-time status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get real-time status",
        )


@router.get("/sessions")
async def get_active_sessions(current_user: User = Depends(get_current_user)):
    """Get active streaming sessions (requires authentication)"""
    try:
        # This would need to be implemented in the streaming service
        # For now, return basic info
        stats = await realtime_streaming_service.get_service_stats()

        return {
            "active_sessions": stats.get("active_sessions", 0),
            "total_connections": stats.get("active_connections", 0),
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get active sessions",
        )


@router.get("/sessions/{session_id}")
async def get_session_status(session_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a specific session (requires authentication)"""
    try:
        # This would need to be implemented in the streaming service
        # For now, return basic info
        return {"session_id": session_id, "status": "active", "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session status",
        )


@router.post("/sessions/{session_id}/broadcast")
async def broadcast_to_session(
    session_id: str,
    message: Dict[str, Any],
    current_user: User = Depends(get_current_user),
):
    """Broadcast message to all connections in a session (requires authentication)"""
    try:
        await realtime_streaming_service.broadcast_to_session(session_id, message)

        return {
            "message": "Broadcast sent successfully",
            "session_id": session_id,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error broadcasting to session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast message",
        )


@router.get("/kafka/status")
async def get_kafka_status(current_user: User = Depends(get_current_user)):
    """Get Kafka streaming service status (requires authentication)"""
    try:
        stats = await kafka_stream_service.get_processing_stats()

        return {
            "status": "active" if kafka_stream_service.producer else "inactive",
            "stats": stats,
            "topics": {
                "audio_topic": kafka_stream_service.audio_topic,
                "transcription_topic": kafka_stream_service.transcription_topic,
            },
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error getting Kafka status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Kafka status",
        )


@router.get("/grpc/status")
async def get_grpc_status(current_user: User = Depends(get_current_user)):
    """Get gRPC service status (requires authentication)"""
    try:
        return {
            "status": "active" if grpc_server.server else "inactive",
            "port": 50051,
            "services": [
                "AudioStreamingService",
                "TextStreamingService",
                "AudioProcessingService",
            ],
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error getting gRPC status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get gRPC status",
        )


@router.post("/test/audio-stream")
async def test_audio_stream(
    session_id: str = "test-session",
    user_id: str = "test-user",
    current_user: User = Depends(get_current_user),
):
    """Test audio streaming functionality (requires authentication)"""
    try:
        # Send test audio chunk to Kafka
        test_audio_data = b"fake audio data for testing"

        success = await kafka_stream_service.send_audio_chunk(
            session_id=session_id,
            user_id=user_id,
            audio_data=test_audio_data,
            sample_rate=16000,
            channels=1,
            format="wav",
            language="en",
            chunk_index=0,
            is_final=True,
        )

        return {
            "message": "Test audio stream sent successfully" if success else "Failed to send test audio stream",
            "session_id": session_id,
            "success": success,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error testing audio stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test audio stream",
        )


@router.get("/metrics")
async def get_realtime_metrics():
    """Get real-time streaming metrics"""
    try:
        stats = await realtime_streaming_service.get_service_stats()
        kafka_stats = await kafka_stream_service.get_processing_stats()

        return {
            "websocket_metrics": {
                "active_connections": stats.get("active_connections", 0),
                "active_sessions": stats.get("active_sessions", 0),
                "total_connections": stats.get("total_connections", 0),
                "total_audio_chunks": stats.get("total_audio_chunks", 0),
                "total_transcriptions": stats.get("total_transcriptions", 0),
                "average_processing_time": stats.get("average_processing_time", 0.0),
            },
            "kafka_metrics": {
                "total_chunks_processed": kafka_stats.get("total_chunks_processed", 0),
                "successful_transcriptions": kafka_stats.get("successful_transcriptions", 0),
                "failed_transcriptions": kafka_stats.get("failed_transcriptions", 0),
                "average_processing_time": kafka_stats.get("average_processing_time", 0.0),
                "active_sessions": kafka_stats.get("active_sessions", 0),
            },
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get real-time metrics",
        )


@router.post("/cleanup/session/{session_id}")
async def cleanup_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Clean up a streaming session (requires authentication)"""
    try:
        await kafka_stream_service.cleanup_session(session_id)

        return {
            "message": "Session cleaned up successfully",
            "session_id": session_id,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup session",
        )
