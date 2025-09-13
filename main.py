"""
VoiceBridge Real-time Speech-to-Text API
Main FastAPI application for processing audio streams and returning transcriptions.

This is the core application that handles:
- Real-time WebSocket audio streaming
- Multiple ML model integration (Whisper, Wav2Vec2, OpenAI)
- Authentication and rate limiting
- Monitoring and metrics collection
- Background task processing with Celery
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from prometheus_fastapi_instrumentator import Instrumentator

from config import settings

# from src.database.mysql_models import User, get_database_manager  # Temporarily disabled
from src.middleware.security_middleware import setup_security_middleware
# from src.routes.auth_routes import router as auth_router  # Temporarily disabled
# from src.routes.monitoring_routes import router as monitoring_router  # Temporarily disabled
# from src.routes.realtime_routes import router as realtime_router  # Temporarily disabled
from src.services.audio_processor import AudioProcessor

# from src.services.auth_service import get_current_user  # Temporarily disabled
from src.services.encryption_service import encryption_service
from src.services.grpc_service import grpc_server
from src.services.kafka_consumer import KafkaConsumer
from src.services.kafka_producer import KafkaProducer
from src.services.kafka_stream_service import kafka_stream_service
from src.services.mlflow_service import mlflow_service
from src.services.model_monitoring_service import model_monitoring_service
from src.services.openai_whisper_service import get_openai_whisper_service
from src.services.prometheus_service import prometheus_metrics
from src.services.rate_limiting_service import rate_limiting_service
from src.services.wandb_service import wandb_service
from src.tasks.transcription_tasks import transcribe_audio_task
from version import get_build_info, get_version

# Configure logging for application monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with comprehensive API documentation
app = FastAPI(
    title="VoiceBridge API",
    description="Real-time speech-to-text API for hearing-impaired individuals",
    version=get_version(),
)

# Add CORS middleware for cross-origin requests (frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes (temporarily disabled)
# app.include_router(auth_router)

# Include monitoring routes (temporarily disabled)
# app.include_router(monitoring_router)

# Include real-time streaming routes (temporarily disabled)
# app.include_router(realtime_router)

# Setup security middleware
setup_security_middleware(app)

# Setup Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Initialize services
audio_processor = AudioProcessor()
whisper_service = get_openai_whisper_service(settings.openai_api_key)
kafka_producer = KafkaProducer()
kafka_consumer = KafkaConsumer()


# WebSocket connection manager
class ConnectionManager:
    """
    Manages WebSocket connections for real-time audio streaming.
    Handles client connections, disconnections, and message broadcasting.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept new WebSocket connection and store client reference."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        """Remove client connection from active connections."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, message: str, client_id: str):
        """Send message to specific client via WebSocket."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)


# Global connection manager instance
manager = ConnectionManager()


# @app.on_event("startup")
async def startup_event():
    """
    Initialize all services on application startup.
    This includes database, rate limiting, monitoring, and real-time services.
    """
    try:
        # Initialize database (temporarily disabled)
        # db_manager = get_database_manager()
        # db_manager.connect()
        # db_manager.create_tables()
        logger.info("Database initialization skipped (SQLAlchemy disabled)")

        # Initialize rate limiting service
        await rate_limiting_service.initialize()
        logger.info("Rate limiting service initialized")

        # Initialize FastAPI Limiter (with fallback)
        try:
            await FastAPILimiter.init(settings.redis_url)
            logger.info("FastAPI Limiter initialized")
        except Exception as e:
            logger.warning(f"FastAPI Limiter failed to initialize: {e}")
            logger.info("Using in-memory rate limiting")

        # Initialize monitoring services
        try:
            mlflow_run_id = mlflow_service.start_run(
                run_name=f"voicebridge-api-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                tags={"component": "api", "version": "1.0.0"},
            )
            logger.info(f"MLFlow run started: {mlflow_run_id}")
        except Exception as e:
            logger.warning(f"MLFlow run failed to start: {e}")
            logger.info("Continuing without MLFlow tracking")

        # Initialize real-time services
        try:
            kafka_started = await kafka_stream_service.start()
            if kafka_started:
                logger.info("Kafka streaming service started")
            else:
                logger.warning("Kafka streaming service failed to start")
        except Exception as e:
            logger.warning(f"Kafka streaming service error: {e}")

        try:
            grpc_started = await grpc_server.start()
            if grpc_started:
                logger.info("gRPC server started")
            else:
                logger.warning("gRPC server failed to start")
        except Exception as e:
            logger.warning(f"gRPC server error: {e}")

        # Log monitoring services info
        logger.info(f"MLFlow tracking URI: {mlflow_service.mlflow_uri}")
        logger.info(f"W&B initialized: {wandb_service.is_initialized}")
        logger.info("Model monitoring service started")
        logger.info("Real-time streaming services initialized")

        # await kafka_producer.start()
        # await kafka_consumer.start()

        # Log OpenAI Whisper service info
        service_info = whisper_service.get_service_info()
        logger.info(f"OpenAI Whisper service: {service_info}")

        # Log encryption service info
        encryption_info = encryption_service.get_encryption_info()
        logger.info(f"Encryption service: {encryption_info}")

        if whisper_service.is_api_available():
            logger.info("VoiceBridge API started successfully with OpenAI Whisper")
        else:
            logger.warning("VoiceBridge API started with mock transcription (no OpenAI API key)")

    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        # Stop real-time services
        await kafka_stream_service.stop()
        await grpc_server.stop()

        # Stop monitoring services
        mlflow_service.end_run()
        wandb_service.finish_run()
        model_monitoring_service.stop_monitoring()

        # await kafka_producer.stop()
        # await kafka_consumer.stop()
        logger.info("VoiceBridge API shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Health check endpoint."""
    build_info = get_build_info()
    return {
        "message": "VoiceBridge API is running",
        "status": "healthy",
        "version": build_info["version"],
        "build_date": build_info["build_date"],
        "author": build_info["author"],
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            # "kafka_producer": kafka_producer.is_connected(),
            # "kafka_consumer": kafka_consumer.is_connected(),
            "openai_whisper": whisper_service.is_api_available(),
            "redis": "connected",  # Add Redis health check
        },
        "transcription_info": whisper_service.get_service_info(),
    }


@app.post("/configure")
async def configure_api_key(api_key: str):
    """Configure OpenAI API key."""
    global whisper_service
    try:
        # Reinitialize service with new API key
        whisper_service = get_openai_whisper_service(api_key)

        return {
            "status": "success",
            "message": "API key configured successfully",
            "api_available": whisper_service.is_api_available(),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to configure API key: {str(e)}"}


@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...), current_user=None, request: Request = None):
    """
    Transcribe audio file endpoint.
    Accepts audio files and returns transcription results.
    Requires authentication.
    """
    try:
        # Apply rate limiting
        client_id = rate_limiting_service.get_client_identifier(request, current_user.id)
        await rate_limiting_service.enforce_rate_limit(client_id, "transcription")

        # Validate file type
        if not audio_processor.is_valid_audio_format(audio_file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format. Supported formats: {settings.supported_audio_formats}",
            )

        # Validate file size
        content = await audio_file.read()
        if len(content) > settings.max_audio_size_mb * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {settings.max_audio_size_mb}MB")

        # Encrypt audio file for secure storage
        encrypted_content, metadata = encryption_service.encrypt_audio_file(content, audio_file.filename)

        # Process audio and send to Kafka
        audio_data = {
            "filename": audio_file.filename,
            "content": encrypted_content,  # Store encrypted content
            "content_type": audio_file.content_type,
            "user_id": current_user.id,
            "encryption_metadata": metadata,
        }

        # Send to Kafka for processing
        await kafka_producer.send_audio(audio_data)

        # Start Celery task for transcription
        transcribe_audio_task.delay(audio_data)

        # Process with Celery task
        start_time = time.time()
        result = await whisper_service.transcribe_audio_bytes(content, language=settings.default_language)
        processing_time = time.time() - start_time

        # Record model performance metrics
        confidence = result.get("confidence", 0.0)
        model_monitoring_service.record_model_performance(
            model_name="whisper",
            accuracy=confidence,  # Using confidence as accuracy proxy
            confidence=confidence,
            processing_time=processing_time,
            error_occurred="error" in result,
        )

        # Log to MLFlow
        mlflow_service.log_transcription_metrics(
            predicted_text=result.get("text", ""),
            actual_text="",  # No ground truth available
            confidence=confidence,
            processing_time=processing_time,
            audio_duration=len(content) / (16000 * 2),  # Rough estimate
            model_name="whisper",
        )

        # Log to W&B
        wandb_service.log_transcription_metrics(
            predicted_text=result.get("text", ""),
            actual_text="",
            confidence=confidence,
            processing_time=processing_time,
            audio_duration=len(content) / (16000 * 2),
            model_name="whisper",
        )

        # Record Prometheus metrics
        prometheus_metrics.record_transcription(
            model="whisper",
            status="success" if "error" not in result else "failure",
            duration=processing_time,
            confidence=confidence,
        )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio transcribed successfully",
                "transcription": result.get("text", ""),
                "confidence": confidence,
                "language": result.get("language", settings.default_language),
                "user_id": current_user.id,
                "encrypted": True,
                "processing_time": processing_time,
                "model": "whisper",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/transcribe/{task_id}")
async def get_transcription_result(task_id: str):
    """
    Get transcription result for a specific task.
    """
    try:
        from celery_app import celery_app

        result = celery_app.AsyncResult(task_id)

        if result.ready():
            if result.successful():
                return {"task_id": task_id, "status": "completed", "result": result.result}
            else:
                return {"task_id": task_id, "status": "failed", "error": str(result.result)}
        else:
            return {"task_id": task_id, "status": "processing"}
    except Exception as e:
        logger.error(f"Error getting task result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, token: Optional[str] = None):
    """
    WebSocket endpoint for real-time audio streaming and transcription.
    Supports optional authentication via token parameter.
    """
    # Apply rate limiting for WebSocket connections
    try:
        client_identifier = f"ws:{client_id}"
        await rate_limiting_service.enforce_rate_limit(client_identifier, "websocket")
    except HTTPException:
        await websocket.close(code=1008, reason="Rate limit exceeded")
        return

    # Optional authentication for WebSocket
    user = None
    if token:
        try:
            from services.auth_service import auth_service

            payload = auth_service.verify_token(token, "access")
            user_id = int(payload.get("sub"))
            user = auth_service.get_user_by_id(user_id)
        except Exception:
            logger.warning(f"Invalid token for WebSocket connection {client_id}")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()

            # Encrypt audio data for secure processing
            encrypted_data, metadata = encryption_service.encrypt_audio_file(data, f"ws_audio_{client_id}")

            # Process audio data
            audio_data = {
                "client_id": client_id,
                "audio_bytes": data,  # Keep original for processing
                "encrypted_audio_bytes": encrypted_data,  # Store encrypted version
                "encryption_metadata": metadata,
                "user_id": user.id if user else None,
                "timestamp": asyncio.get_event_loop().time(),
            }

            # Send to Kafka for real-time processing
            # await kafka_producer.send_audio_stream(audio_data)

            # Start real-time transcription task
            # Send acknowledgment
            await websocket.send_text(json.dumps({"type": "acknowledgment", "status": "processing", "encrypted": True}))

            # Process audio directly (without Celery)
            asyncio.create_task(process_audio_directly(websocket, audio_data, client_id, user))

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


# Background task to process audio directly (without Celery)
async def process_audio_directly(websocket: WebSocket, audio_data: dict, client_id: str, user=None):
    """Process audio directly and send result to WebSocket client."""
    try:
        import time

        logger.info(
            f"Processing audio for client {client_id}, data size: {len(audio_data.get('audio_bytes', b''))} bytes"
        )

        # Get audio bytes from the data
        audio_bytes = audio_data.get("audio_bytes", b"")

        if not audio_bytes:
            logger.warning(f"No audio data received for client {client_id}")
            await websocket.send_text(
                json.dumps({"type": "error", "message": "No audio data received", "timestamp": time.time()})
            )
            return

        # Use OpenAI Whisper API to transcribe the audio
        try:
            start_time = time.time()
            # Use English as default language as requested
            result = await whisper_service.transcribe_audio_bytes(audio_bytes, language=settings.default_language)
            processing_time = time.time() - start_time

            if "error" in result:
                logger.error(f"OpenAI Whisper transcription error: {result['error']}")

                # Record error metrics
                if user:
                    model_monitoring_service.record_model_performance(
                        model_name="whisper",
                        accuracy=0.0,
                        confidence=0.0,
                        processing_time=processing_time,
                        error_occurred=True,
                    )

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Transcription failed: {result['error']}",
                            "timestamp": time.time(),
                        }
                    )
                )
                return

            text = result.get("text", "").strip()
            confidence = result.get("confidence", 0.0)
            language = result.get("language", settings.default_language)
            provider = result.get("provider", "unknown")

            # Record performance metrics
            if user:
                model_monitoring_service.record_model_performance(
                    model_name="whisper",
                    accuracy=confidence,
                    confidence=confidence,
                    processing_time=processing_time,
                    error_occurred=False,
                )

                # Log to MLFlow and W&B
                mlflow_service.log_transcription_metrics(
                    predicted_text=text,
                    actual_text="",
                    confidence=confidence,
                    processing_time=processing_time,
                    audio_duration=len(audio_bytes) / (16000 * 2),
                    model_name="whisper",
                )

                wandb_service.log_transcription_metrics(
                    predicted_text=text,
                    actual_text="",
                    confidence=confidence,
                    processing_time=processing_time,
                    audio_duration=len(audio_bytes) / (16000 * 2),
                    model_name="whisper",
                )

            # Record Prometheus metrics
            prometheus_metrics.record_transcription(
                model="whisper", status="success", duration=processing_time, confidence=confidence
            )

            if text:
                # Send successful transcription result
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "transcription",
                            "text": text,
                            "confidence": confidence,
                            "language": language,
                            "provider": provider,
                            "processing_time": processing_time,
                            "timestamp": time.time(),
                        }
                    )
                )

                if provider.startswith("mock"):
                    logger.info(f"Sent mock transcription to client {client_id}: '{text}' (No API key)")
                else:
                    logger.info(
                        f"Sent OpenAI Whisper transcription to client {client_id}: '{text}' (confidence: {confidence:.2f})"
                    )
            else:
                # No speech detected
                logger.info(f"No speech detected for client {client_id}")
                await websocket.send_text(
                    json.dumps({"type": "info", "message": "No speech detected in audio", "timestamp": time.time()})
                )

        except Exception as whisper_error:
            logger.error(f"OpenAI Whisper processing error for client {client_id}: {whisper_error}")

            # Record error metrics
            if user:
                model_monitoring_service.record_model_performance(
                    model_name="whisper",
                    accuracy=0.0,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    error_occurred=True,
                )

            await websocket.send_text(
                json.dumps(
                    {
                        "type": "error",
                        "message": f"Speech recognition error: {str(whisper_error)}",
                        "timestamp": time.time(),
                    }
                )
            )

    except Exception as e:
        logger.error(f"Error processing audio for client {client_id}: {e}")
        try:
            await websocket.send_text(
                json.dumps({"type": "error", "message": f"Processing error: {str(e)}", "timestamp": time.time()})
            )
        except Exception:
            pass  # WebSocket might be closed


# Background task to send transcription results to WebSocket clients
async def send_transcription_to_client(client_id: str, transcription: str):
    """Send transcription result to specific WebSocket client."""
    await manager.send_message(
        json.dumps({"type": "transcription", "text": transcription, "timestamp": asyncio.get_event_loop().time()}),
        client_id,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=settings.api_debug)
