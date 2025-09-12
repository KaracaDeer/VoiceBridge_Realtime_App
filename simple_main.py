"""
VoiceBridge Real-time Speech-to-Text API - Simplified Version
Basic FastAPI application for testing startup without complex dependencies.
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VoiceBridge API - Simple",
    description="Real-time speech-to-text API for hearing-impaired individuals (Simplified)",
    version="1.0.0-simple",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("VoiceBridge API (Simple) started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("VoiceBridge API (Simple) shutdown complete")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "VoiceBridge API (Simple) is running",
        "status": "healthy",
        "version": "1.0.0-simple",
        "build_date": datetime.utcnow().isoformat(),
        "author": "VoiceBridge Team",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "services": {"api": "running", "websockets": "available"},
        "active_connections": len(manager.active_connections),
    }


@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """
    Mock transcribe audio file endpoint.
    Returns a mock transcription for testing.
    """
    try:
        # Validate file type
        if not audio_file.filename.lower().endswith((".wav", ".mp3", ".m4a", ".flac", ".webm")):
            raise HTTPException(
                status_code=400, detail="Unsupported audio format. Supported formats: wav, mp3, m4a, flac, webm"
            )

        # Read file content
        content = await audio_file.read()

        # Validate file size (10MB max)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size: 10MB")

        # Mock transcription
        mock_transcription = f"Mock transcription for file: {audio_file.filename}"
        processing_time = 0.5  # Mock processing time

        return JSONResponse(
            status_code=200,
            content={
                "message": "Audio transcribed successfully (MOCK)",
                "transcription": mock_transcription,
                "confidence": 0.95,
                "language": "en",
                "processing_time": processing_time,
                "model": "mock-whisper",
                "file_size": len(content),
                "filename": audio_file.filename,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time audio streaming and transcription (mock).
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()

            # Send acknowledgment
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "acknowledgment",
                        "status": "processing",
                        "client_id": client_id,
                        "data_size": len(data),
                        "timestamp": time.time(),
                    }
                )
            )

            # Mock processing delay
            await asyncio.sleep(0.1)

            # Send mock transcription
            mock_text = f"Mock transcription for client {client_id} - received {len(data)} bytes"
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "transcription",
                        "text": mock_text,
                        "confidence": 0.95,
                        "language": "en",
                        "provider": "mock-whisper",
                        "processing_time": 0.1,
                        "timestamp": time.time(),
                    }
                )
            )

            logger.info(f"Sent mock transcription to client {client_id}: '{mock_text}'")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


if __name__ == "__main__":
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
