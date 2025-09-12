"""
Celery tasks for audio transcription processing.
"""
import io
import logging
import time
from typing import Any, Dict

import librosa
import numpy as np
import speech_recognition as sr

from celery_app import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize speech recognizer
recognizer = sr.Recognizer()


@celery_app.task(bind=True, name="transcribe_audio_task")
def transcribe_audio_task(self, audio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task for transcribing audio data.

    Args:
        audio_data: Dictionary containing audio information and content

    Returns:
        Dictionary with transcription results
    """
    try:
        # Update task progress
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Processing audio"})

        start_time = time.time()

        # Extract audio content
        if "content" in audio_data:
            # File upload case
            audio_bytes = audio_data["content"]
            filename = audio_data.get("filename", "unknown")
        elif "audio_bytes" in audio_data:
            # Real-time stream case
            audio_bytes = audio_data["audio_bytes"]
            filename = f"stream_{audio_data.get('client_id', 'unknown')}"
        else:
            raise ValueError("No audio content found in audio_data")

        self.update_state(state="PROGRESS", meta={"progress": 30, "status": "Loading audio"})

        # Load and preprocess audio
        audio_array, sample_rate = load_audio_from_bytes(audio_bytes)

        self.update_state(state="PROGRESS", meta={"progress": 50, "status": "Transcribing audio"})

        # Perform transcription
        transcription_result = transcribe_audio(audio_array, sample_rate)

        self.update_state(state="PROGRESS", meta={"progress": 80, "status": "Finalizing results"})

        processing_time = time.time() - start_time

        # Prepare result
        result = {
            "transcription": transcription_result["text"],
            "confidence": transcription_result["confidence"],
            "language": "en",  # English only as specified
            "processing_time": processing_time,
            "filename": filename,
            "sample_rate": sample_rate,
            "audio_duration": len(audio_array) / sample_rate,
            "status": "completed",
        }

        # If this is a real-time stream, include client_id
        if "client_id" in audio_data:
            result["client_id"] = audio_data["client_id"]

        self.update_state(state="SUCCESS", meta={"progress": 100, "result": result})

        logger.info(f"Transcription completed for {filename} in {processing_time:.2f}s")
        return result

    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        logger.error(error_msg)

        self.update_state(state="FAILURE", meta={"error": error_msg, "status": "failed"})

        return {"error": error_msg, "status": "failed", "transcription": None}


def load_audio_from_bytes(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    """
    Load audio from bytes and return audio array and sample rate.

    Args:
        audio_bytes: Raw audio data

    Returns:
        Tuple of (audio_array, sample_rate)
    """
    try:
        # Create a BytesIO object from the audio bytes
        audio_io = io.BytesIO(audio_bytes)

        # Load audio using librosa
        audio_array, sample_rate = librosa.load(audio_io, sr=None, mono=True)

        # Resample to 16kHz if needed (optimal for speech recognition)
        if sample_rate != 16000:
            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000

        return audio_array, int(sample_rate)

    except Exception as e:
        logger.error(f"Error loading audio: {e}")
        raise ValueError(f"Failed to load audio: {e}")


def transcribe_audio(audio_array: np.ndarray, sample_rate: int) -> Dict[str, Any]:
    """
    Transcribe audio array using speech recognition.

    Args:
        audio_array: Audio data as numpy array
        sample_rate: Sample rate of the audio

    Returns:
        Dictionary with transcription text and confidence
    """
    try:
        # Convert numpy array to AudioData for speech_recognition
        audio_data = sr.AudioData(
            audio_array.tobytes(),
            sample_rate,
            sample_rate * 2,  # 2 bytes per sample (16-bit)
        )

        # Perform transcription using Google Speech Recognition
        # Note: In production, you might want to use a more robust service
        # or implement your own speech recognition model
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            confidence = 0.8  # Google doesn't provide confidence, using default

        except sr.UnknownValueError:
            text = ""
            confidence = 0.0
            logger.warning("Could not understand audio")

        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            # Fallback to offline recognition or return empty result
            text = ""
            confidence = 0.0

        return {"text": text, "confidence": confidence}

    except Exception as e:
        logger.error(f"Error during transcription: {e}")
        return {"text": "", "confidence": 0.0}


@celery_app.task(name="batch_transcribe_task")
def batch_transcribe_task(audio_files: list) -> Dict[str, Any]:
    """
    Batch transcription task for multiple audio files.

    Args:
        audio_files: List of audio file data

    Returns:
        Dictionary with batch transcription results
    """
    results = []

    for i, audio_data in enumerate(audio_files):
        try:
            # Process each file
            result = transcribe_audio_task.delay(audio_data)
            results.append({"index": i, "task_id": result.id, "status": "processing"})
        except Exception as e:
            results.append({"index": i, "error": str(e), "status": "failed"})

    return {
        "batch_id": f"batch_{int(time.time())}",
        "total_files": len(audio_files),
        "results": results,
        "status": "processing",
    }
