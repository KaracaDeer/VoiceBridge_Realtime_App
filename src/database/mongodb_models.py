"""
MongoDB Models for VoiceBridge
Flexible document storage for conversations, audio metadata, and unstructured data
"""
import logging
from datetime import datetime
from typing import Any, Dict

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class MongoDBManager:
    """MongoDB database manager"""

    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        """
        Initialize MongoDB manager

        Args:
            connection_string: MongoDB connection string
        """
        self.connection_string = connection_string
        self.client = None
        self.db = None

    def connect(self, database_name: str = "voicebridge"):
        """
        Establish MongoDB connection

        Args:
            database_name: Name of the database to use
        """
        try:
            self.client = MongoClient(self.connection_string)
            if self.client is not None:
                self.db = self.client[database_name]
            else:
                logger.error("Failed to create MongoDB client")
                return False

            # Test connection
            if self.client is not None:
                self.client.admin.command("ping")
            logger.info(f"MongoDB connected to database: {database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


class ConversationDocument:
    """Document structure for conversation storage"""

    @staticmethod
    def create_conversation(user_id: str, session_id: str, title: str = None, language: str = "en") -> Dict[str, Any]:
        """
        Create a new conversation document

        Args:
            user_id: User identifier
            session_id: Session identifier
            title: Conversation title
            language: Language code

        Returns:
            Conversation document
        """
        return {
            "_id": None,  # Will be set by MongoDB
            "user_id": user_id,
            "session_id": session_id,
            "title": title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "language": language,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",  # active, completed, archived
            "messages": [],
            "metadata": {
                "total_messages": 0,
                "total_duration": 0.0,
                "average_confidence": 0.0,
                "languages_detected": [language],
            },
        }

    @staticmethod
    def add_message(
        conversation: Dict[str, Any],
        message_type: str,
        content: str,
        confidence: float = 0.0,
        audio_metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Add a message to conversation

        Args:
            conversation: Conversation document
            message_type: Type of message (user_speech, system_response, etc.)
            content: Message content
            confidence: Confidence score
            audio_metadata: Audio file metadata

        Returns:
            Updated conversation document
        """
        message = {
            "id": len(conversation["messages"]) + 1,
            "type": message_type,
            "content": content,
            "confidence": confidence,
            "timestamp": datetime.utcnow(),
            "audio_metadata": audio_metadata or {},
        }

        conversation["messages"].append(message)
        conversation["updated_at"] = datetime.utcnow()
        conversation["metadata"]["total_messages"] += 1

        # Update average confidence
        total_confidence = sum(msg["confidence"] for msg in conversation["messages"])
        conversation["metadata"]["average_confidence"] = total_confidence / len(conversation["messages"])

        return conversation


class AudioMetadataDocument:
    """Document structure for audio file metadata"""

    @staticmethod
    def create_audio_metadata(
        file_id: str,
        user_id: str,
        session_id: str,
        file_path: str,
        file_size: int,
        duration: float,
        sample_rate: int,
        channels: int,
        format: str,
    ) -> Dict[str, Any]:
        """
        Create audio metadata document

        Args:
            file_id: Unique file identifier
            user_id: User identifier
            session_id: Session identifier
            file_path: Path to audio file
            file_size: File size in bytes
            duration: Audio duration in seconds
            sample_rate: Sample rate
            channels: Number of channels
            format: Audio format (wav, mp3, etc.)

        Returns:
            Audio metadata document
        """
        return {
            "_id": file_id,
            "user_id": user_id,
            "session_id": session_id,
            "file_path": file_path,
            "file_size": file_size,
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": channels,
            "format": format,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "uploaded",  # uploaded, processed, archived, deleted
            "processing_info": {
                "transcription_completed": False,
                "features_extracted": False,
                "model_used": None,
                "processing_time": 0.0,
            },
            "quality_metrics": {
                "snr": None,  # Signal-to-noise ratio
                "clarity": None,
                "background_noise": None,
            },
        }


class MLModelDocument:
    """Document structure for ML model metadata"""

    @staticmethod
    def create_model_metadata(
        model_name: str,
        model_type: str,
        version: str,
        performance_metrics: Dict[str, Any],
        training_data_info: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Create ML model metadata document

        Args:
            model_name: Name of the model
            model_type: Type of model (wav2vec2, whisper, etc.)
            version: Model version
            performance_metrics: Model performance metrics
            training_data_info: Information about training data

        Returns:
            Model metadata document
        """
        return {
            "_id": f"{model_name}_{version}",
            "model_name": model_name,
            "model_type": model_type,
            "version": version,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",  # active, deprecated, training
            "performance_metrics": performance_metrics,
            "training_data_info": training_data_info or {},
            "deployment_info": {
                "environment": "production",
                "instance_count": 1,
                "resource_usage": {
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "gpu_usage": 0.0,
                },
            },
            "usage_statistics": {
                "total_predictions": 0,
                "average_processing_time": 0.0,
                "success_rate": 0.0,
                "error_rate": 0.0,
            },
        }


class AnalyticsDocument:
    """Document structure for analytics and reporting"""

    @staticmethod
    def create_daily_analytics(
        date: str,
        total_users: int,
        total_transcriptions: int,
        total_audio_duration: float,
        average_confidence: float,
        language_distribution: Dict[str, int],
        model_performance: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create daily analytics document

        Args:
            date: Date in YYYY-MM-DD format
            total_users: Total active users
            total_transcriptions: Total transcriptions processed
            total_audio_duration: Total audio duration processed
            average_confidence: Average confidence score
            language_distribution: Distribution of languages
            model_performance: Model performance metrics

        Returns:
            Daily analytics document
        """
        return {
            "_id": f"analytics_{date}",
            "date": date,
            "created_at": datetime.utcnow(),
            "metrics": {
                "users": {
                    "total_active": total_users,
                    "new_registrations": 0,
                    "returning_users": 0,
                },
                "transcriptions": {
                    "total_count": total_transcriptions,
                    "successful": 0,
                    "failed": 0,
                    "average_processing_time": 0.0,
                },
                "audio": {
                    "total_duration": total_audio_duration,
                    "average_duration": 0.0,
                    "total_size_bytes": 0,
                },
                "quality": {
                    "average_confidence": average_confidence,
                    "high_confidence_rate": 0.0,  # > 0.8
                    "low_confidence_rate": 0.0,  # < 0.5
                },
                "languages": language_distribution,
                "models": model_performance,
            },
        }


# Global MongoDB manager instance
_mongodb_manager = None


def get_mongodb_manager(connection_string: str = None) -> MongoDBManager:
    """Get MongoDB manager instance"""
    global _mongodb_manager
    if _mongodb_manager is None:
        if connection_string is None:
            connection_string = "mongodb://localhost:27017/"
        _mongodb_manager = MongoDBManager(connection_string)
    return _mongodb_manager
