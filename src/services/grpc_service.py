"""
gRPC service for VoiceBridge API
Handles high-performance real-time audio streaming and transcription
"""
# type: ignore
import asyncio
import logging
import threading
import time
from concurrent import futures
from typing import Any, AsyncIterator, Dict, Optional

import grpc

# Import generated protobuf classes (will be generated from proto file)
try:
    import os
    import sys

    # Add current directory to path
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from proto import voicebridge_pb2  # type: ignore
    from proto import voicebridge_pb2_grpc  # type: ignore
except ImportError:
    # Fallback to root-level generated files if available
    try:
        import voicebridge_pb2  # type: ignore
        import voicebridge_pb2_grpc  # type: ignore
    except ImportError:
        logging.warning("gRPC protobuf files not found. Running in mock mode.")
        voicebridge_pb2 = None  # type: ignore
        voicebridge_pb2_grpc = None  # type: ignore

from config import settings
from src.services.model_monitoring_service import model_monitoring_service
from src.services.openai_whisper_service import get_openai_whisper_service

logger = logging.getLogger(__name__)


class AudioStreamingServicer(object):  # type: ignore
    """gRPC servicer for audio streaming"""

    def __init__(self):
        self.whisper_service = get_openai_whisper_service(settings.openai_api_key)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.subscriber_queue: Optional[Any] = None  # type: ignore
        self.session_lock = threading.Lock()

    async def StreamAudio(self, request_iterator: AsyncIterator, context) -> AsyncIterator:
        """Stream audio data for real-time transcription"""
        session_id = None
        user_id = None
        audio_buffer = b""
        buffer_size = 0
        max_buffer_size = 1024 * 1024  # 1MB buffer

        try:
            async for audio_chunk in request_iterator:
                if not session_id:
                    session_id = audio_chunk.session_id
                    user_id = audio_chunk.user_id

                    # Initialize session
                    with self.session_lock:
                        self.active_sessions[session_id] = {
                            "user_id": user_id,
                            "start_time": time.time(),
                            "chunks_processed": 0,
                            "total_audio_duration": 0.0,
                        }

                    logger.info(f"Started gRPC audio stream for session {session_id}")

                # Accumulate audio data
                audio_buffer += audio_chunk.audio_data
                buffer_size += len(audio_chunk.audio_data)

                # Process when buffer is full or on timeout
                if buffer_size >= max_buffer_size or len(audio_buffer) > 0:
                    start_time = time.time()

                    try:
                        # Process audio chunk
                        result = await self.whisper_service.transcribe_audio_bytes(
                            audio_buffer,
                            language=audio_chunk.language or settings.default_language,
                        )

                        processing_time = time.time() - start_time

                        # Record metrics
                        model_monitoring_service.record_model_performance(
                            model_name="whisper_grpc",
                            accuracy=result.get("confidence", 0.0),
                            confidence=result.get("confidence", 0.0),
                            processing_time=processing_time,
                            error_occurred="error" in result,
                        )

                        # Update session stats
                        with self.session_lock:
                            if session_id in self.active_sessions:
                                self.active_sessions[session_id]["chunks_processed"] += 1
                                self.active_sessions[session_id]["total_audio_duration"] += processing_time

                        # Create response
                        if voicebridge_pb2:
                            response = voicebridge_pb2.TranscriptionResult(
                                session_id=session_id,
                                user_id=user_id,
                                text=result.get("text", ""),
                                confidence=result.get("confidence", 0.0),
                                language=result.get("language", settings.default_language),
                                timestamp=int(time.time() * 1000),
                                status=voicebridge_pb2.TranscriptionStatus.COMPLETED
                                if "error" not in result
                                else voicebridge_pb2.TranscriptionStatus.FAILED,
                                model_name="whisper",
                                processing_time=processing_time,
                            )

                            yield response

                        # Clear buffer
                        audio_buffer = b""
                        buffer_size = 0

                    except Exception as e:
                        logger.error(f"Error processing audio chunk: {e}")

                        if voicebridge_pb2:
                            error_response = voicebridge_pb2.TranscriptionResult(
                                session_id=session_id,
                                user_id=user_id,
                                text="",
                                confidence=0.0,
                                language=settings.default_language,
                                timestamp=int(time.time() * 1000),
                                status=voicebridge_pb2.TranscriptionStatus.FAILED,
                                model_name="whisper",
                                processing_time=0.0,
                            )

                            yield error_response

        except Exception as e:
            logger.error(f"Error in StreamAudio: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")

        finally:
            # Clean up session
            if session_id:
                with self.session_lock:
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                logger.info(f"Ended gRPC audio stream for session {session_id}")

    async def GetTranscriptionStatus(self, request, context):
        """Get transcription status for a session"""
        session_id = request.session_id

        with self.session_lock:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]

                if voicebridge_pb2:
                    return voicebridge_pb2.TranscriptionStatus(
                        session_id=session_id,
                        user_id=session_data["user_id"],
                        status=voicebridge_pb2.TranscriptionStatus.PROCESSING,
                        chunks_processed=session_data["chunks_processed"],
                        total_duration=session_data["total_audio_duration"],
                    )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Session not found")
                return None

    async def HealthCheck(self, request, context):
        """Health check endpoint"""
        if voicebridge_pb2:
            return voicebridge_pb2.HealthResponse(
                healthy=True,
                status="OK",
                version="1.0.0",
                timestamp=int(time.time() * 1000),
            )
        return None


class TextStreamingServicer(object):
    """gRPC servicer for text streaming"""

    def __init__(self):
        self.text_subscribers: Dict[str, list] = {}
        self.subscriber_lock = threading.Lock()

    async def StreamText(self, request_iterator: AsyncIterator, context) -> AsyncIterator:
        """Stream text results to clients"""
        try:
            async for text_request in request_iterator:
                session_id = text_request.session_id
                # user_id = text_request.user_id  # Currently not used

                # Broadcast to subscribers
                with self.subscriber_lock:
                    if session_id in self.text_subscribers:
                        for subscriber in self.text_subscribers[session_id]:
                            try:
                                await subscriber.put(text_request)
                            except Exception as e:
                                logger.error(f"Error broadcasting to subscriber: {e}")

                # Send acknowledgment
                if voicebridge_pb2:
                    response = voicebridge_pb2.TextStreamResponse(
                        session_id=session_id,
                        success=True,
                        message="Text streamed successfully",
                        timestamp=int(time.time() * 1000),
                    )
                    yield response

        except Exception as e:
            logger.error(f"Error in StreamText: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")

    async def SubscribeToText(self, request, context) -> AsyncIterator:
        """Subscribe to text updates"""
        session_id = request.session_id
        user_id = request.user_id

        # Create subscriber queue
        subscriber_queue = asyncio.Queue()

        # Add to subscribers
        with self.subscriber_lock:
            if session_id not in self.text_subscribers:
                self.text_subscribers[session_id] = []
            self.text_subscribers[session_id].append(subscriber_queue)

        try:
            while True:
                # Wait for text updates
                text_request = await subscriber_queue.get()

                if voicebridge_pb2:
                    text_update = voicebridge_pb2.TextUpdate(
                        session_id=session_id,
                        user_id=user_id,
                        text=text_request.text,
                        confidence=text_request.confidence,
                        language=settings.default_language,
                        timestamp=text_request.timestamp,
                        type=voicebridge_pb2.UpdateType.NEW_TEXT,
                    )

                    yield text_update

        except asyncio.CancelledError:
            logger.info(f"Text subscription cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in SubscribeToText: {e}")
        finally:
            # Remove from subscribers
            with self.subscriber_lock:
                if session_id in self.text_subscribers:
                    if subscriber_queue in self.text_subscribers[session_id]:
                        self.text_subscribers[session_id].remove(subscriber_queue)


class AudioProcessingServicer(object):
    """gRPC servicer for audio processing"""

    def __init__(self):
        self.whisper_service = get_openai_whisper_service(settings.openai_api_key)
        self.processing_stats: Dict[str, Dict[str, Any]] = {}
        self.stats_lock = threading.Lock()

    async def ProcessAudioChunk(self, request, context):
        """Process a single audio chunk"""
        start_time = time.time()
        session_id = request.session_id
        user_id = request.user_id

        try:
            # Process audio
            result = await self.whisper_service.transcribe_audio_bytes(
                request.audio_data,
                language=request.language or settings.default_language,
            )

            processing_time = time.time() - start_time

            # Update stats
            with self.stats_lock:
                if session_id not in self.processing_stats:
                    self.processing_stats[session_id] = {
                        "total_chunks": 0,
                        "successful_chunks": 0,
                        "failed_chunks": 0,
                        "total_processing_time": 0.0,
                        "total_confidence": 0.0,
                    }

                stats = self.processing_stats[session_id]
                stats["total_chunks"] += 1
                stats["total_processing_time"] += processing_time

                if "error" not in result:
                    stats["successful_chunks"] += 1
                    stats["total_confidence"] += result.get("confidence", 0.0)
                else:
                    stats["failed_chunks"] += 1

            # Create response
            if voicebridge_pb2:
                transcription_result = voicebridge_pb2.TranscriptionResult(
                    session_id=session_id,
                    user_id=user_id,
                    text=result.get("text", ""),
                    confidence=result.get("confidence", 0.0),
                    language=result.get("language", settings.default_language),
                    timestamp=int(time.time() * 1000),
                    status=voicebridge_pb2.TranscriptionStatus.COMPLETED
                    if "error" not in result
                    else voicebridge_pb2.TranscriptionStatus.FAILED,
                    model_name="whisper",
                    processing_time=processing_time,
                )

                return voicebridge_pb2.ProcessingResult(
                    session_id=session_id,
                    user_id=user_id,
                    success="error" not in result,
                    error_message=result.get("error", ""),
                    processing_time=processing_time,
                    transcription=transcription_result,
                    timestamp=int(time.time() * 1000),
                )

        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Processing error: {str(e)}")

            if voicebridge_pb2:
                return voicebridge_pb2.ProcessingResult(
                    session_id=session_id,
                    user_id=user_id,
                    success=False,
                    error_message=str(e),
                    processing_time=time.time() - start_time,
                    timestamp=int(time.time() * 1000),
                )

    async def BatchProcessAudio(self, request_iterator: AsyncIterator, context) -> AsyncIterator:
        """Batch process multiple audio chunks"""
        try:
            async for audio_chunk in request_iterator:
                # Process each chunk
                result = await self.ProcessAudioChunk(audio_chunk, context)
                yield result

        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Batch processing error: {str(e)}")

    async def GetProcessingStats(self, request, context):
        """Get processing statistics"""
        session_id = request.session_id

        with self.stats_lock:
            if session_id in self.processing_stats:
                stats = self.processing_stats[session_id]

                if voicebridge_pb2:
                    return voicebridge_pb2.ProcessingStats(
                        total_chunks=stats["total_chunks"],
                        successful_chunks=stats["successful_chunks"],
                        failed_chunks=stats["failed_chunks"],
                        average_processing_time=stats["total_processing_time"] / max(stats["total_chunks"], 1),
                        average_confidence=stats["total_confidence"] / max(stats["successful_chunks"], 1),
                        total_audio_duration=stats["total_processing_time"],
                    )
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("No statistics found for session")
                return None


class GRPCServer:
    """gRPC server for VoiceBridge API"""

    def __init__(self, port: int = 50051):
        self.port = port
        self.server = None
        self.audio_servicer = AudioStreamingServicer()
        self.text_servicer = TextStreamingServicer()
        self.processing_servicer = AudioProcessingServicer()

    async def start(self):
        """Start the gRPC server"""
        if not voicebridge_pb2_grpc:
            logger.error("gRPC protobuf files not available")
            return False

        try:
            self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))

            # Add servicers (only if protobuf files are available)
            if voicebridge_pb2_grpc:
                voicebridge_pb2_grpc.add_AudioStreamingServiceServicer_to_server(self.audio_servicer, self.server)
                voicebridge_pb2_grpc.add_TextStreamingServiceServicer_to_server(self.text_servicer, self.server)
                voicebridge_pb2_grpc.add_AudioProcessingServiceServicer_to_server(self.processing_servicer, self.server)
            else:
                logger.warning("gRPC protobuf files not available. Running in mock mode.")
                return False

            # Add health check
            from grpc_health.v1 import health_pb2_grpc
            from grpc_health.v1.health import HealthServicer

            health_servicer = HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)

            # Start server
            listen_addr = f"[::]:{self.port}"
            self.server.add_insecure_port(listen_addr)
            await self.server.start()

            logger.info(f"gRPC server started on port {self.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start gRPC server: {e}")
            return False

    async def stop(self):
        """Stop the gRPC server"""
        if self.server:
            await self.server.stop(grace=5.0)
            logger.info("gRPC server stopped")


# Global gRPC server instance
grpc_server = GRPCServer()
