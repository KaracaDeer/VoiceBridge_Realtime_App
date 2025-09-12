"""
Simple VoiceBridge Backend with WAV support
"""
import asyncio
import json
import logging

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="VoiceBridge API", version="1.0.0")

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


manager = ConnectionManager()


async def transcribe_audio_simple(audio_data: bytes) -> str:
    """Simple audio transcription function with WAV support."""
    try:
        # Basic validation
        if len(audio_data) < 5000:  # Less than 5KB
            size_kb = len(audio_data) / 1024
            return f"Audio too short ({size_kb:.1f}KB) - Speak longer"

        size_kb = len(audio_data) / 1024

        # Check if it's WAV format (starts with RIFF)
        if audio_data.startswith(b"RIFF") and b"WAVE" in audio_data[:20]:
            # This is WAV format - try speech recognition
            try:
                import os
                import tempfile

                import speech_recognition as sr

                # Create recognizer
                recognizer = sr.Recognizer()

                # Save WAV data to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_path = temp_file.name

                try:
                    # Try to recognize speech
                    with sr.AudioFile(temp_path) as source:
                        audio = recognizer.record(source)
                        text = recognizer.recognize_google(audio, language="tr-TR")
                        return f"🎤 Speech recognized: {text}"
                except sr.UnknownValueError:
                    return f"Audio detected ({size_kb:.1f}KB) but not understood - Speak more clearly"
                except sr.RequestError as e:
                    return f"Google Speech API error: {str(e)}"
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass

            except ImportError:
                return f"Audio detected ({size_kb:.1f}KB) - SpeechRecognition library not installed"
            except Exception as e:
                return f"WAV processing error: {str(e)}"
        else:
            # Not WAV format - try to process as WebM or other formats
            try:
                import os
                import tempfile

                import speech_recognition as sr

                # Create recognizer
                recognizer = sr.Recognizer()

                # Try different extensions
                extensions = [".webm", ".ogg", ".opus", ".m4a"]

                for ext in extensions:
                    try:
                        # Save data to temporary file
                        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
                            temp_file.write(audio_data)
                            temp_path = temp_file.name

                        # Try to use speech recognition directly
                        try:
                            with sr.AudioFile(temp_path) as source:
                                audio = recognizer.record(source)
                                text = recognizer.recognize_google(audio, language="tr-TR")
                                return f"🎤 Speech recognized: {text}"
                        except sr.UnknownValueError:
                            continue  # Try next format
                        except Exception:
                            continue  # Try next format
                        finally:
                            # Clean up temp file
                            try:
                                os.unlink(temp_path)
                            except Exception:
                                pass
                    except Exception:
                        continue

                # If all formats failed
                return f"Audio detected ({size_kb:.1f}KB) - Format not supported, speak clearly"

            except ImportError:
                return f"Audio detected ({size_kb:.1f}KB) - SpeechRecognition library not installed"
            except Exception as e:
                return f"WebM processing error: {str(e)}"

    except Exception as e:
        return f"Transcription error: {str(e)}"


@app.get("/")
async def root():
    return {"message": "VoiceBridge API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voicebridge-api"}


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive binary data (audio)
            data = await websocket.receive_bytes()
            logger.info(f"Received audio data from {client_id}: {len(data)} bytes")

            # Send acknowledgment
            await websocket.send_text(json.dumps({"type": "acknowledgment", "status": "processing"}))

            # Process audio for transcription
            try:
                # Try to transcribe the audio
                transcription_text = await transcribe_audio_simple(data)

                # Send transcription result
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "transcription",
                            "text": transcription_text,
                            "confidence": 0.95,
                            "timestamp": asyncio.get_event_loop().time(),
                        }
                    )
                )

            except Exception as e:
                logger.error(f"Error processing audio for {client_id}: {e}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Processing error: {str(e)}",
                            "timestamp": asyncio.get_event_loop().time(),
                        }
                    )
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
