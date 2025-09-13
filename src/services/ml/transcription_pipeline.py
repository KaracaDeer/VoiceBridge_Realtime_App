"""
Modular transcription pipeline for ML services.
Handles audio preprocessing, model inference, and post-processing.
"""
import logging
import time
from typing import Any, Dict, Optional

import numpy as np

from .model_manager import ModelManager
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class TranscriptionPipeline:
    """Modular transcription pipeline for audio processing."""

    def __init__(self, model_manager: Optional[ModelManager] = None, 
                 performance_monitor: Optional[PerformanceMonitor] = None):
        """
        Initialize transcription pipeline.
        
        Args:
            model_manager: Model manager instance
            performance_monitor: Performance monitoring instance
        """
        self.model_manager = model_manager or ModelManager()
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        
        logger.info("TranscriptionPipeline initialized")

    async def transcribe_audio(self, audio_bytes: bytes, 
                              language: str = "en",
                              model_name: str = "whisper") -> Dict[str, Any]:
        """
        Transcribe audio using the configured pipeline.
        
        Args:
            audio_bytes: Raw audio data
            language: Language code
            model_name: Model to use for transcription
            
        Returns:
            Transcription result dictionary
        """
        start_time = time.time()
        
        try:
            # Step 1: Preprocess audio
            preprocessed_audio = await self._preprocess_audio(audio_bytes)
            
            # Step 2: Run model inference
            transcription_result = await self._run_inference(
                preprocessed_audio, language, model_name
            )
            
            # Step 3: Post-process results
            final_result = await self._postprocess_results(
                transcription_result, language, model_name
            )
            
            # Record performance metrics
            processing_time = time.time() - start_time
            await self.performance_monitor.record_transcription_metrics(
                model_name=model_name,
                processing_time=processing_time,
                confidence=final_result.get("confidence", 0.0),
                success="error" not in final_result
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Transcription pipeline error: {e}")
            return {
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "language": language,
                "model": model_name,
                "processing_time": time.time() - start_time
            }

    async def _preprocess_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """
        Preprocess audio data for model input.
        
        Args:
            audio_bytes: Raw audio data
            
        Returns:
            Preprocessed audio data
        """
        try:
            # Basic audio preprocessing
            # In a real implementation, this would include:
            # - Noise reduction
            # - Normalization
            # - Format conversion
            # - Feature extraction
            
            return {
                "audio_bytes": audio_bytes,
                "preprocessed": True,
                "duration": len(audio_bytes) / (16000 * 2),  # Rough estimate
                "sample_rate": 16000
            }
            
        except Exception as e:
            logger.error(f"Audio preprocessing error: {e}")
            return {
                "audio_bytes": audio_bytes,
                "preprocessed": False,
                "error": str(e)
            }

    async def _run_inference(self, preprocessed_audio: Dict[str, Any], 
                           language: str, model_name: str) -> Dict[str, Any]:
        """
        Run model inference on preprocessed audio.
        
        Args:
            preprocessed_audio: Preprocessed audio data
            language: Language code
            model_name: Model to use
            
        Returns:
            Model inference result
        """
        try:
            # Get model from manager
            model = await self.model_manager.get_model(model_name)
            
            if not model:
                return {
                    "error": f"Model {model_name} not available",
                    "text": "",
                    "confidence": 0.0
                }
            
            # Run inference
            result = await model.transcribe(
                preprocessed_audio["audio_bytes"], 
                language=language
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Model inference error: {e}")
            return {
                "error": str(e),
                "text": "",
                "confidence": 0.0
            }

    async def _postprocess_results(self, inference_result: Dict[str, Any], 
                                 language: str, model_name: str) -> Dict[str, Any]:
        """
        Post-process model inference results.
        
        Args:
            inference_result: Raw model output
            language: Language code
            model_name: Model used
            
        Returns:
            Final transcription result
        """
        try:
            # Basic post-processing
            # In a real implementation, this would include:
            # - Text normalization
            # - Confidence calibration
            # - Language-specific corrections
            
            final_result = {
                "text": inference_result.get("text", "").strip(),
                "confidence": inference_result.get("confidence", 0.0),
                "language": language,
                "model": model_name,
                "provider": inference_result.get("provider", "unknown")
            }
            
            # Add error if present
            if "error" in inference_result:
                final_result["error"] = inference_result["error"]
            
            return final_result
            
        except Exception as e:
            logger.error(f"Post-processing error: {e}")
            return {
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "language": language,
                "model": model_name
            }

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get pipeline configuration and status."""
        return {
            "pipeline_type": "modular_transcription",
            "model_manager": self.model_manager.get_manager_info(),
            "performance_monitor": self.performance_monitor.get_monitor_info(),
            "available_models": self.model_manager.get_available_models()
        }
