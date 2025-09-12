"""
Whisper-based Speech-to-Text Service
Real-time audio transcription using OpenAI Whisper
"""
import logging
import os
import tempfile
from typing import Any, Dict, List

import numpy as np
import torch
import whisper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperService:
    """Service for speech-to-text transcription using OpenAI Whisper."""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper service.

        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
                       - tiny: ~1GB, fastest but lower accuracy
                       - base: ~1GB, good balance of speed and accuracy
                       - small: ~2GB, better accuracy
                       - medium: ~5GB, very good accuracy
                       - large: ~10GB, best accuracy but slower
        """
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper model '{self.model_size}' loaded successfully")

            # Check if CUDA is available
            if torch.cuda.is_available():
                logger.info("CUDA is available, using GPU acceleration")
            else:
                logger.info("CUDA not available, using CPU")

        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "tr") -> Dict[str, Any]:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Raw audio data as bytes
            language: Target language code ('tr' for Turkish, 'en' for English, None for auto-detect)

        Returns:
            Dictionary with transcription results
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            try:
                # Transcribe using Whisper
                result = self._transcribe_file(temp_file_path, language)
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "error": str(e),
            }

    def transcribe_audio_file(self, file_path: str, language: str = "tr") -> Dict[str, Any]:
        """
        Transcribe audio from file path.

        Args:
            file_path: Path to audio file
            language: Target language code

        Returns:
            Dictionary with transcription results
        """
        try:
            return self._transcribe_file(file_path, language)
        except Exception as e:
            logger.error(f"Error transcribing audio file {file_path}: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "error": str(e),
            }

    def _transcribe_file(self, file_path: str, language: str = "tr") -> Dict[str, Any]:
        """
        Internal method to transcribe audio file.

        Args:
            file_path: Path to audio file
            language: Target language code

        Returns:
            Dictionary with transcription results
        """
        try:
            if not self.model:
                raise ValueError("Whisper model not loaded")

            # Transcribe with Whisper
            if language and language != "auto":
                result = self.model.transcribe(file_path, language=language, word_timestamps=True, verbose=False)
            else:
                # Auto-detect language
                result = self.model.transcribe(file_path, word_timestamps=True, verbose=False)

            # Extract text and calculate confidence
            text = result.get("text", "").strip()
            detected_language = result.get("language", language)

            # Calculate average confidence from segments
            segments = result.get("segments", [])
            if segments:
                # Whisper doesn't provide confidence directly, so we estimate based on probability
                total_prob = sum(segment.get("avg_logprob", -1.0) for segment in segments)
                avg_logprob = total_prob / len(segments) if segments else -1.0
                # Convert log probability to confidence (rough estimation)
                confidence = max(0.0, min(1.0, np.exp(avg_logprob + 1.0)))
            else:
                confidence = 0.8 if text else 0.0  # Default confidence if no segments

            logger.info(f"Transcription result: '{text}' (confidence: {confidence:.2f}, language: {detected_language})")

            return {
                "text": text,
                "confidence": confidence,
                "language": detected_language,
                "segments": segments,
                "duration": result.get("duration", 0),
                "words": self._extract_words(segments),
            }

        except Exception as e:
            logger.error(f"Error in _transcribe_file: {e}")
            raise

    def _extract_words(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract words with timestamps from segments.

        Args:
            segments: List of transcription segments

        Returns:
            List of words with timestamps
        """
        words = []
        for segment in segments:
            segment_words = segment.get("words", [])
            for word in segment_words:
                words.append(
                    {
                        "word": word.get("word", "").strip(),
                        "start": word.get("start", 0),
                        "end": word.get("end", 0),
                        "probability": word.get("probability", 0.5),
                    }
                )
        return words

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.

        Returns:
            List of supported language codes
        """
        # Whisper supports these languages well
        return [
            "tr",  # Turkish
            "en",  # English
            "es",  # Spanish
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ru",  # Russian
            "ja",  # Japanese
            "ko",  # Korean
            "zh",  # Chinese
            "ar",  # Arabic
            "hi",  # Hindi
            "auto",  # Auto-detect
        ]

    def is_model_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self.model is not None

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model."""
        return {
            "model_size": self.model_size,
            "is_loaded": str(self.is_model_loaded()),
            "cuda_available": str(torch.cuda.is_available()),
            "device": "cuda" if torch.cuda.is_available() else "cpu",
        }


# Global instance (singleton pattern)
_whisper_service = None


def get_whisper_service(model_size: str = "base") -> WhisperService:
    """
    Get global Whisper service instance.

    Args:
        model_size: Whisper model size

    Returns:
        WhisperService instance
    """
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService(model_size)
    return _whisper_service
