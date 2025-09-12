"""
Wav2Vec2 Speech Recognition Service
Speech recognition service using Wav2Vec2 model with Hugging Face Transformers
"""
import io
import logging
from typing import Any, Dict

import numpy as np
import soundfile as sf
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

logger = logging.getLogger(__name__)


class Wav2Vec2Service:
    """Wav2Vec2-based speech recognition service"""

    def __init__(self, model_name: str = "facebook/wav2vec2-base-960h"):
        """
        Initialize Wav2Vec2 service

        Args:
            model_name: Hugging Face model name
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_loaded = False

        logger.info(f"Wav2Vec2Service initialized with device: {self.device}")

    def load_model(self) -> bool:
        """Load and prepare the model"""
        try:
            logger.info(f"Loading Wav2Vec2 model: {self.model_name}")

            # Load model and processor
            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            self.model = Wav2Vec2ForCTC.from_pretrained(self.model_name)

            # Move model to appropriate device
            if self.model is not None:
                self.model.to(self.device)
                self.model.eval()

            self.is_loaded = True
            logger.info(f"Wav2Vec2 model loaded successfully on {self.device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Wav2Vec2 model: {e}")
            self.is_loaded = False
            return False

    def preprocess_audio(self, audio_bytes: bytes, target_sample_rate: int = 16000) -> torch.Tensor:
        """
        Preprocess audio data

        Args:
            audio_bytes: Raw audio data
            target_sample_rate: Target sample rate

        Returns:
            Preprocessed audio tensor
        """
        try:
            # Convert audio data to numpy array
            audio_array, sample_rate = sf.read(io.BytesIO(audio_bytes))

            # Convert to mono (if stereo)
            if len(audio_array.shape) > 1:
                audio_array = np.mean(audio_array, axis=1)

            # Adjust sample rate
            if sample_rate != target_sample_rate:
                resampler = torchaudio.transforms.Resample(sample_rate, target_sample_rate)
                audio_tensor = torch.from_numpy(audio_array).float()
                audio_tensor = resampler(audio_tensor)
            else:
                audio_tensor = torch.from_numpy(audio_array).float()

            # Normalize
            audio_tensor = audio_tensor / torch.max(torch.abs(audio_tensor))

            return audio_tensor

        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise

    def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Convert audio data to text

        Args:
            audio_bytes: Raw audio data
            language: Language code

        Returns:
            Transcription result
        """
        if not self.is_loaded:
            if not self.load_model():
                return {
                    "error": "Model could not be loaded",
                    "text": "",
                    "confidence": 0.0,
                }

        try:
            # Preprocess audio data
            audio_tensor = self.preprocess_audio(audio_bytes)

            # Tokenize with processor
            if self.processor is not None:
                input_values = self.processor(audio_tensor, sampling_rate=16000, return_tensors="pt").input_values.to(
                    self.device
                )
            else:
                raise RuntimeError("Processor not loaded")

            # Make prediction with model
            with torch.no_grad():
                if self.model is not None:
                    logits = self.model(input_values).logits
                else:
                    raise RuntimeError("Model not loaded")

            # CTC decoding
            predicted_ids = torch.argmax(logits, dim=-1)
            if self.processor is not None:
                transcription = self.processor.decode(predicted_ids[0])
            else:
                raise RuntimeError("Processor not loaded")

            # Calculate confidence score (simple approach)
            confidence = torch.softmax(logits, dim=-1).max().item()

            logger.info(f"Wav2Vec2 transcription completed: '{transcription}' (confidence: {confidence:.3f})")

            return {
                "text": transcription.strip(),
                "confidence": confidence,
                "language": language,
                "provider": "Wav2Vec2",
                "model": self.model_name,
            }

        except Exception as e:
            logger.error(f"Wav2Vec2 transcription failed: {e}")
            return {"error": str(e), "text": "", "confidence": 0.0}

    def get_service_info(self) -> Dict[str, Any]:
        """Return service information"""
        return {
            "provider": "Wav2Vec2",
            "model": self.model_name,
            "device": str(self.device),
            "is_loaded": self.is_loaded,
            "supported_languages": [
                "en",
                "tr",
                "es",
                "fr",
                "de",
                "it",
                "pt",
                "ru",
                "ja",
                "ko",
                "zh",
            ],
        }

    def is_available(self) -> bool:
        """Check if service is available"""
        return self.is_loaded


# Global service instance
_wav2vec_service = None


def get_wav2vec_service(
    model_name: str = "facebook/wav2vec2-base-960h",
) -> Wav2Vec2Service:
    """Get Wav2Vec2 service instance"""
    global _wav2vec_service
    if _wav2vec_service is None:
        _wav2vec_service = Wav2Vec2Service(model_name)
    return _wav2vec_service
