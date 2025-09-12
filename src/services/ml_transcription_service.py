"""
ML Transcription Service
Main ML transcription service that combines Wav2Vec2 and preprocessing services
"""
# type: ignore
import logging
from typing import Any, Dict

import numpy as np

from src.services.audio_preprocessing_service import get_preprocessing_service
from src.services.wav2vec_service import get_wav2vec_service

logger = logging.getLogger(__name__)


class MLTranscriptionService:
    """ML-based transcription service"""

    def __init__(self, use_preprocessing: bool = True, use_wav2vec: bool = True):
        """
        Initialize ML transcription service

        Args:
            use_preprocessing: Whether to use preprocessing
            use_wav2vec: Whether to use Wav2Vec2
        """
        self.use_preprocessing = use_preprocessing
        self.use_wav2vec = use_wav2vec

        # Initialize services
        self.wav2vec_service = None
        self.preprocessing_service = None

        if use_wav2vec:
            self.wav2vec_service = get_wav2vec_service()

        if use_preprocessing:
            self.preprocessing_service = get_preprocessing_service()

        logger.info(f"MLTranscriptionService initialized - Preprocessing: {use_preprocessing}, Wav2Vec2: {use_wav2vec}")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Convert audio data to text using ML models

        Args:
            audio_bytes: Raw audio data
            language: Language code

        Returns:
            Transcription result
        """
        try:
            result = {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "provider": "ML Pipeline",
                "preprocessing_used": False,
                "wav2vec_used": False,
                "processing_time": 0.0,
            }

            import time

            start_time = time.time()

            # Preprocessing (optional)
            if self.use_preprocessing and self.preprocessing_service:
                try:
                    preprocessed = self.preprocessing_service.preprocess_audio_bytes(audio_bytes)
                    if preprocessed.get("preprocessing_successful"):
                        result["preprocessing_used"] = True
                        result["audio_duration"] = preprocessed.get("duration", 0.0)
                        result["mfcc_features_shape"] = preprocessed.get("mfcc_features", np.array([])).shape
                        logger.info(f"Audio preprocessing completed: {result['audio_duration']:.2f}s")
                    else:
                        logger.warning(f"Preprocessing failed: {preprocessed.get('error', 'Unknown error')}")
                except Exception as e:
                    logger.warning(f"Preprocessing error: {e}")

            # Wav2Vec2 transcription
            if self.use_wav2vec and self.wav2vec_service:
                try:
                    transcription_result = self.wav2vec_service.transcribe_audio_bytes(audio_bytes, language)

                    if not transcription_result.get("error"):
                        result["text"] = transcription_result.get("text", "")
                        result["confidence"] = transcription_result.get("confidence", 0.0)
                        result["wav2vec_used"] = True
                        result["model"] = transcription_result.get("model", "")
                        logger.info(
                            f"Wav2Vec2 transcription successful: '{result['text']}' (confidence: {result['confidence']:.3f})"
                        )
                    else:
                        logger.error(f"Wav2Vec2 transcription failed: {transcription_result.get('error')}")
                        result["error"] = transcription_result.get("error")

                except Exception as e:
                    logger.error(f"Wav2Vec2 error: {e}")
                    result["error"] = str(e)
            else:
                # Fallback: Simple audio detection
                result["text"] = f"Audio detected ({len(audio_bytes)} bytes) - ML transcription service not active"
                result["confidence"] = 0.5
                result["provider"] = "Fallback"

            # Processing time
            result["processing_time"] = time.time() - start_time

            return result

        except Exception as e:
            logger.error(f"ML transcription failed: {e}")
            return {
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "language": language,
                "provider": "ML Pipeline",
            }

    def get_service_info(self) -> Dict[str, Any]:
        """Return service information"""
        info = {
            "provider": "ML Pipeline",
            "use_preprocessing": self.use_preprocessing,
            "use_wav2vec": self.use_wav2vec,
            "services": {},
        }

        if self.wav2vec_service:
            wav2vec_info = self.wav2vec_service.get_service_info()
            if isinstance(wav2vec_info, dict):
                services_dict = info["services"]
                services_dict["wav2vec"] = wav2vec_info

        if self.preprocessing_service:
            preprocessing_info = {
                "provider": "Audio Preprocessing",
                "features": ["MFCC", "Spectral", "Normalization"],
                "is_available": True,
            }
            services_dict = info["services"]
            services_dict["preprocessing"] = preprocessing_info

        return info

    def is_available(self) -> bool:
        """Check if service is available"""
        if self.use_wav2vec and self.wav2vec_service:
            return self.wav2vec_service.is_available()
        return True  # Preprocessing is always available


# Global service instance
_ml_transcription_service = None


def get_ml_transcription_service(use_preprocessing: bool = True, use_wav2vec: bool = True) -> MLTranscriptionService:
    """Get ML transcription service instance"""
    global _ml_transcription_service
    if _ml_transcription_service is None:
        _ml_transcription_service = MLTranscriptionService(use_preprocessing, use_wav2vec)
    return _ml_transcription_service
