"""
OpenAI Whisper API Service
Real-time audio transcription using OpenAI's Whisper API

This service provides high-quality speech-to-text transcription using OpenAI's
Whisper model. It supports multiple languages and provides confidence scores.

Key features:
- Multi-language support (English, Turkish, and many others)
- High accuracy transcription
- Confidence scoring
- Fallback to mock responses when API key is not available
- Async/await support for non-blocking operations
"""
import asyncio
import logging
import os
import tempfile
from typing import Any, Dict, Optional

from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIWhisperService:
    """Service for speech-to-text transcription using OpenAI Whisper API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI Whisper service.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Service will use mock responses.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI Whisper API service initialized successfully")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio from bytes using OpenAI Whisper API.

        Args:
            audio_bytes: Raw audio data as bytes
            language: Target language code ('en' for English, 'tr' for Turkish, etc.)

        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            return await self._mock_transcription(language)

        try:
            # Create temporary file with appropriate extension
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            try:
                # Call OpenAI Whisper API
                with open(temp_file_path, "rb") as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                        response_format="verbose_json",
                    )

                # Extract results
                text = transcript.text.strip()
                duration = getattr(transcript, "duration", 0)
                segments = getattr(transcript, "segments", [])

                # Calculate confidence (OpenAI doesn't provide this directly)
                confidence = 0.9 if text else 0.0  # High confidence for successful transcriptions

                logger.info(f"OpenAI Whisper transcription: '{text}' (language: {language})")

                return {
                    "text": text,
                    "confidence": confidence,
                    "language": language,
                    "duration": duration,
                    "segments": segments,
                    "provider": "openai_whisper",
                }

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error transcribing audio with OpenAI Whisper: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "error": str(e),
                "provider": "openai_whisper",
            }

    async def transcribe_audio_file(self, file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio from file path using OpenAI Whisper API.

        Args:
            file_path: Path to audio file
            language: Target language code

        Returns:
            Dictionary with transcription results
        """
        if not self.client:
            return await self._mock_transcription(language)

        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                )

            text = transcript.text.strip()
            duration = getattr(transcript, "duration", 0)
            segments = getattr(transcript, "segments", [])
            confidence = 0.9 if text else 0.0

            logger.info(f"OpenAI Whisper file transcription: '{text}'")

            return {
                "text": text,
                "confidence": confidence,
                "language": language,
                "duration": duration,
                "segments": segments,
                "provider": "openai_whisper",
            }

        except Exception as e:
            logger.error(f"Error transcribing file {file_path}: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "error": str(e),
                "provider": "openai_whisper",
            }

    async def _mock_transcription(self, language: str = "en") -> Dict[str, Any]:
        """
        Provide mock transcription when API key is not available.

        Args:
            language: Target language code

        Returns:
            Mock transcription result
        """
        import random

        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 1.5))

        if language == "en":
            mock_responses = [
                "Hello, this is a test transcription.",
                "VoiceBridge application is working properly.",
                "Speech recognition system is now active.",
                "Audio transcription test successful.",
                "Real-time voice to text conversion.",
                "Microphone test: Audio levels are good.",
                "English speech recognition is working.",
                "Welcome to VoiceBridge speech-to-text.",
                "Your voice is being processed correctly.",
            ]
        else:  # Turkish fallback
            mock_responses = [
                "Hello, this is a test transcription message.",
                "VoiceBridge application is working properly.",
                "Speech recognition system is now active.",
                "Speech transcription test successful.",
                "Real-time speech to text conversion.",
                "Microphone test: Audio levels are good.",
            ]

        response_text = random.choice(mock_responses)
        confidence = random.uniform(0.85, 0.95)

        return {
            "text": response_text,
            "confidence": confidence,
            "language": language,
            "provider": "mock_openai_whisper",
            "note": "This is a mock response. Please set OPENAI_API_KEY for real transcription.",
        }

    def is_api_available(self) -> bool:
        """Check if OpenAI API is available (API key provided)."""
        return self.client is not None

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service."""
        return {
            "provider": "OpenAI Whisper API",
            "api_available": self.is_api_available(),
            "model": "whisper-1",
            "supported_languages": self.get_supported_languages(),
        }

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages by OpenAI Whisper.

        Returns:
            List of supported language codes
        """
        return [
            "en",  # English
            "tr",  # Turkish
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
            "nl",  # Dutch
            "sv",  # Swedish
            "no",  # Norwegian
            "da",  # Danish
            "fi",  # Finnish
            "pl",  # Polish
            "cs",  # Czech
            "hu",  # Hungarian
            "ro",  # Romanian
            "bg",  # Bulgarian
            "hr",  # Croatian
            "sk",  # Slovak
            "sl",  # Slovenian
            "et",  # Estonian
            "lv",  # Latvian
            "lt",  # Lithuanian
            "uk",  # Ukrainian
            "be",  # Belarusian
            "mk",  # Macedonian
            "mt",  # Maltese
            "is",  # Icelandic
            "ga",  # Irish
            "cy",  # Welsh
            "eu",  # Basque
            "ca",  # Catalan
            "gl",  # Galician
            "ast",  # Asturian
            "an",  # Aragonese
            "oc",  # Occitan
            "br",  # Breton
            "co",  # Corsican
            "fy",  # Frisian
            "rm",  # Romansh
            "sc",  # Sardinian
            "vec",  # Venetian
            "wa",  # Walloon
            "yi",  # Yiddish
            "he",  # Hebrew
            "fa",  # Persian
            "ur",  # Urdu
            "ps",  # Pashto
            "ky",  # Kyrgyz
            "kk",  # Kazakh
            "uz",  # Uzbek
            "tg",  # Tajik
            "mn",  # Mongolian
            "bo",  # Tibetan
            "my",  # Burmese
            "th",  # Thai
            "lo",  # Lao
            "km",  # Khmer
            "vi",  # Vietnamese
            "id",  # Indonesian
            "ms",  # Malay
            "tl",  # Filipino
            "haw",  # Hawaiian
            "mi",  # Maori
            "cy",  # Welsh
            "mt",  # Maltese
            "sq",  # Albanian
            "mk",  # Macedonian
            "bg",  # Bulgarian
            "hr",  # Croatian
            "sr",  # Serbian
            "bs",  # Bosnian
            "me",  # Montenegrin
            "sl",  # Slovenian
        ]


# Global instance (singleton pattern)
_whisper_api_service = None


def get_openai_whisper_service(api_key: Optional[str] = None) -> OpenAIWhisperService:
    """
    Get global OpenAI Whisper service instance.

    Args:
        api_key: OpenAI API key

    Returns:
        OpenAIWhisperService instance
    """
    global _whisper_api_service
    if _whisper_api_service is None:
        _whisper_api_service = OpenAIWhisperService(api_key)
    return _whisper_api_service
