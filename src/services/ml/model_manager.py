"""
Model manager for handling different ML models.
Manages model loading, caching, and switching.
"""
import logging
from typing import Any, Dict, List, Optional

from ..openai_whisper_service import get_openai_whisper_service
from ..wav2vec_service import get_wav2vec_service

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models for transcription."""

    def __init__(self):
        """Initialize model manager."""
        self.models: Dict[str, Any] = {}
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        self._initialize_models()
        
        logger.info("ModelManager initialized")

    def _initialize_models(self):
        """Initialize available models."""
        try:
            # Initialize Whisper model
            self.models["whisper"] = get_openai_whisper_service()
            self.model_configs["whisper"] = {
                "type": "openai",
                "model_name": "whisper-1",
                "languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                "max_audio_duration": 25 * 60,  # 25 minutes
                "supports_streaming": True
            }
            
            # Initialize Wav2Vec2 model
            try:
                self.models["wav2vec"] = get_wav2vec_service()
                self.model_configs["wav2vec"] = {
                    "type": "local",
                    "model_name": "wav2vec2-base-960h",
                    "languages": ["en"],
                    "max_audio_duration": 10 * 60,  # 10 minutes
                    "supports_streaming": False
                }
            except Exception as e:
                logger.warning(f"Wav2Vec2 model not available: {e}")
                
            logger.info(f"Initialized {len(self.models)} models: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")

    async def get_model(self, model_name: str) -> Optional[Any]:
        """
        Get model instance by name.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model instance or None if not found
        """
        return self.models.get(model_name)

    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.models.keys())

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model configuration.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration or None if not found
        """
        return self.model_configs.get(model_name)

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if model is available.
        
        Args:
            model_name: Name of the model
            
        Returns:
            True if model is available
        """
        return model_name in self.models

    def get_model_capabilities(self, model_name: str) -> Dict[str, Any]:
        """
        Get model capabilities.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model capabilities dictionary
        """
        config = self.get_model_config(model_name)
        if not config:
            return {}
            
        return {
            "supported_languages": config.get("languages", []),
            "max_audio_duration": config.get("max_audio_duration", 0),
            "supports_streaming": config.get("supports_streaming", False),
            "model_type": config.get("type", "unknown")
        }

    async def switch_model(self, from_model: str, to_model: str) -> bool:
        """
        Switch from one model to another.
        
        Args:
            from_model: Current model name
            to_model: Target model name
            
        Returns:
            True if switch was successful
        """
        try:
            if not self.is_model_available(to_model):
                logger.error(f"Target model {to_model} not available")
                return False
                
            # In a real implementation, this would handle model switching
            # For now, just log the switch
            logger.info(f"Switching from {from_model} to {to_model}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching models: {e}")
            return False

    def get_manager_info(self) -> Dict[str, Any]:
        """Get model manager information."""
        return {
            "total_models": len(self.models),
            "available_models": self.get_available_models(),
            "model_configs": {
                name: {
                    "type": config.get("type"),
                    "model_name": config.get("model_name"),
                    "languages": config.get("languages", []),
                    "supports_streaming": config.get("supports_streaming", False)
                }
                for name, config in self.model_configs.items()
            }
        }

    async def reload_model(self, model_name: str) -> bool:
        """
        Reload a specific model.
        
        Args:
            model_name: Name of the model to reload
            
        Returns:
            True if reload was successful
        """
        try:
            if model_name not in self.models:
                logger.error(f"Model {model_name} not found")
                return False
                
            # Reload model based on type
            if model_name == "whisper":
                self.models["whisper"] = get_openai_whisper_service()
            elif model_name == "wav2vec":
                self.models["wav2vec"] = get_wav2vec_service()
                
            logger.info(f"Model {model_name} reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading model {model_name}: {e}")
            return False

    async def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """
        Get model performance metrics.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Performance metrics dictionary
        """
        try:
            model = self.models.get(model_name)
            if not model:
                return {"error": f"Model {model_name} not found"}
                
            # Get model-specific performance info
            if hasattr(model, 'get_service_info'):
                return model.get_service_info()
            else:
                return {
                    "model_name": model_name,
                    "status": "available",
                    "performance_info": "not_available"
                }
                
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {"error": str(e)}
