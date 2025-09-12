"""
VoiceBridge Backend with Database Integration
ML models and database services integrated VoiceBridge backend
"""
import json
import logging
import time

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Import database services
from src.database.data_service import get_data_service
from src.services.audio_preprocessing_service import get_preprocessing_service

# Import ML services
from src.services.ml_transcription_service import get_ml_transcription_service
from src.services.wav2vec_service import get_wav2vec_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="VoiceBridge Database API",
    version="3.0.0",
    description="VoiceBridge API with ML models and database integration",
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

# Initialize services
ml_service = get_ml_transcription_service(use_preprocessing=True, use_wav2vec=True)
wav2vec_service = get_wav2vec_service()
preprocessing_service = get_preprocessing_service()

# Initialize data service (with mock connections for demo)
data_service = get_data_service(
    mysql_connection_string="mysql+mysqlconnector://root:password@localhost:3306/voicebridge",
    mongodb_connection_string="mongodb://localhost:27017/",
)

# Try to connect to databases (will fail gracefully if not available)
try:
    db_connected = data_service.connect_all()
    if db_connected:
        logger.info("Database connections established")
    else:
        logger.warning("Database connections failed - running in demo mode")
except Exception as e:
    logger.warning(f"Database connection failed: {e} - running in demo mode")
    db_connected = False


@app.get("/")
async def root():
    """Home page"""
    return {
        "message": "VoiceBridge Database API is running",
        "version": "3.0.0",
        "features": ["ML Transcription", "Wav2Vec2", "Audio Preprocessing", "Database Integration"],
        "database_status": "connected" if db_connected else "demo_mode",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "services": {
            "ml_transcription": ml_service.is_available(),
            "wav2vec": wav2vec_service.is_available() if wav2vec_service else False,
            "preprocessing": True,
            "database": db_connected,
        },
        "ml_info": ml_service.get_service_info(),
    }


@app.get("/db/status")
async def database_status():
    """Database connection status"""
    return {
        "mysql_connected": data_service.mysql_connected,
        "mongodb_connected": data_service.mongodb_connected,
        "overall_status": "connected" if db_connected else "demo_mode",
    }


@app.post("/users")
async def create_user(user_data: dict):
    """Create a new user"""
    if not db_connected:
        return {"error": "Database not connected", "demo_mode": True}

    try:
        user_id = data_service.create_user(
            username=user_data.get("username"),
            email=user_data.get("email"),
            password_hash=user_data.get("password_hash"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
        )

        if user_id:
            return {"status": "success", "user_id": user_id}
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user information"""
    if not db_connected:
        return {"error": "Database not connected", "demo_mode": True}

    try:
        user = data_service.get_user(user_id=user_id)
        if user:
            return {"status": "success", "user": user}
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/transcriptions")
async def get_user_transcriptions(user_id: int, limit: int = 100):
    """Get user's transcriptions"""
    if not db_connected:
        return {"error": "Database not connected", "demo_mode": True}

    try:
        transcriptions = data_service.get_user_transcriptions(user_id, limit)
        return {"status": "success", "transcriptions": transcriptions}

    except Exception as e:
        logger.error(f"Error getting transcriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Database-enabled WebSocket endpoint"""
    await manager.connect(websocket, client_id)

    # Create conversation in MongoDB if connected
    conversation_id = None
    if db_connected:
        try:
            conversation_id = data_service.create_conversation(
                user_id=f"user_{client_id}", session_id=client_id, title=f"Session {client_id}"
            )
            logger.info(f"Conversation created: {conversation_id}")
        except Exception as e:
            logger.warning(f"Failed to create conversation: {e}")

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
                    # Save transcription to database if connected
                    if db_connected and result.get("text"):
                        try:
                            transcription_data = {
                                "session_id": client_id,
                                "audio_duration": result.get("audio_duration", 0.0),
                                "audio_size_bytes": len(data),
                                "sample_rate": 16000,
                                "original_text": result.get("text", ""),
                                "processed_text": result.get("text", ""),
                                "confidence_score": result.get("confidence", 0.0),
                                "language_detected": result.get("language", "en"),
                                "model_used": result.get("model", ""),
                                "preprocessing_used": result.get("preprocessing_used", False),
                                "processing_time": processing_time,
                                "features": result.get("feature_statistics", {}),
                            }

                            # Save to MySQL
                            transcription_id = data_service.save_transcription(
                                user_id=1, transcription_data=transcription_data  # Demo user ID
                            )

                            # Add message to MongoDB conversation
                            if conversation_id:
                                data_service.add_message_to_conversation(
                                    conversation_id=conversation_id,
                                    message_type="user_speech",
                                    content=result.get("text", ""),
                                    confidence=result.get("confidence", 0.0),
                                )

                            logger.info(f"Transcription saved to database (ID: {transcription_id})")

                        except Exception as e:
                            logger.warning(f"Failed to save transcription to database: {e}")

                    # Send successful transcription
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
                                "saved_to_database": db_connected,
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
    """Test ML services with database integration"""
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

        # Save to database if connected
        transcription_id = None
        if db_connected and result.get("text"):
            try:
                transcription_data = {
                    "session_id": "test_session",
                    "audio_duration": duration,
                    "audio_size_bytes": len(test_audio),
                    "sample_rate": sample_rate,
                    "original_text": result.get("text", ""),
                    "processed_text": result.get("text", ""),
                    "confidence_score": result.get("confidence", 0.0),
                    "language_detected": "en",
                    "model_used": result.get("model", ""),
                    "preprocessing_used": result.get("preprocessing_used", False),
                    "processing_time": result.get("processing_time", 0.0),
                    "features": result.get("feature_statistics", {}),
                }

                transcription_id = data_service.save_transcription(
                    user_id=1, transcription_data=transcription_data  # Demo user ID
                )
            except Exception as e:
                logger.warning(f"Failed to save test transcription: {e}")

        return {
            "status": "success",
            "test_audio_size": len(test_audio),
            "ml_result": result,
            "database_saved": transcription_id is not None,
            "transcription_id": transcription_id,
            "services_info": ml_service.get_service_info(),
        }

    except Exception as e:
        logger.error(f"ML test failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    logger.info("Starting VoiceBridge Database API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
