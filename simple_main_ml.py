"""
VoiceBridge Backend with ML Integration
VoiceBridge backend integrated with ML models
"""
import json
import logging
import time

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.audio_preprocessing_service import get_preprocessing_service

# Import ML services
from services.ml_transcription_service import get_ml_transcription_service
from services.wav2vec_service import get_wav2vec_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VoiceBridge ML API", version="2.0.0", description="VoiceBridge API with ML-powered speech recognition"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

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

# Initialize ML services
ml_service = get_ml_transcription_service(use_preprocessing=True, use_wav2vec=True)
wav2vec_service = get_wav2vec_service()
preprocessing_service = get_preprocessing_service()


@app.get("/")
async def root():
    """Home page"""
    return {
        "message": "VoiceBridge ML API is running",
        "version": "2.0.0",
        "features": ["ML Transcription", "Wav2Vec2", "Audio Preprocessing"],
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "ml_transcription": ml_service.is_available(),
            "wav2vec": wav2vec_service.is_available() if wav2vec_service else False,
            "preprocessing": True,  # Preprocessing is always available
        },
        "ml_info": ml_service.get_service_info(),
    }


@app.get("/ml/info")
async def ml_service_info():
    """Return ML service information"""
    return {
        "ml_service": ml_service.get_service_info(),
        "wav2vec": wav2vec_service.get_service_info() if wav2vec_service else None,
        "preprocessing": {
            "provider": "Audio Preprocessing",
            "features": ["MFCC", "Spectral", "Normalization"],
            "is_available": True,
        },
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """ML-enabled WebSocket endpoint"""
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            logger.info(f"Received audio data from {client_id}: {len(data)} bytes")

            # Send acknowledgment
            await websocket.send_text(
                json.dumps({"type": "acknowledgment", "status": "processing", "timestamp": time.time()})
            )

            # ML speech recognition
            try:
                start_time = time.time()

                # Transcription with ML service
                result = await ml_service.transcribe_audio_bytes(data, language="en")

                processing_time = time.time() - start_time

                if result.get("error"):
                    logger.error(f"ML transcription error: {result['error']}")
                    # Fallback in case of error
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": f"ML transcription failed: {result['error']}",
                                "timestamp": time.time(),
                            }
                        )
                    )
                else:
                    # Successful transcription
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "transcription",
                                "text": result.get("text", ""),
                                "confidence": result.get("confidence", 0.0),
                                "language": result.get("language", "en"),
                                "provider": result.get("provider", "ML Pipeline"),
                                "processing_time": processing_time,
                                "preprocessing_used": result.get("preprocessing_used", False),
                                "wav2vec_used": result.get("wav2vec_used", False),
                                "timestamp": time.time(),
                            }
                        )
                    )

                    logger.info(
                        f"ML transcription completed for {client_id}: '{result.get('text', '')}' (confidence: {result.get('confidence', 0.0):.3f}, time: {processing_time:.2f}s)"
                    )

            except Exception as e:
                logger.error(f"ML transcription error for client {client_id}: {e}")
                # Fallback response
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "transcription",
                            "text": f"Audio detected ({len(data)} bytes) - ML service temporarily unavailable",
                            "confidence": 0.5,
                            "provider": "Fallback",
                            "timestamp": time.time(),
                        }
                    )
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


@app.post("/ml/test")
async def test_ml_services():
    """Test ML services"""
    try:
        # Create test audio (simple sine wave)
        import io

        import numpy as np
        import soundfile as sf

        # 2-second test audio
        sample_rate = 16000
        duration = 2.0
        frequency = 440.0  # A4 note

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        audio_data = audio_data / np.max(np.abs(audio_data))

        # Convert to bytes
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format="WAV")
        test_audio = buffer.getvalue()

        # Test with ML service
        result = await ml_service.transcribe_audio_bytes(test_audio, language="en")

        return {
            "status": "success",
            "test_audio_size": len(test_audio),
            "ml_result": result,
            "services_info": ml_service.get_service_info(),
        }

    except Exception as e:
        logger.error(f"ML test failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    logger.info("Starting VoiceBridge ML API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
