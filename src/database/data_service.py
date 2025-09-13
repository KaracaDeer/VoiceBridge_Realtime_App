"""
Unified Data Service for VoiceBridge
Combines MySQL and MongoDB operations for comprehensive data management
"""
import json
import logging
from typing import Any, Dict, List, Optional

from src.database.mongodb_models import ConversationDocument, get_mongodb_manager

# from src.database.mysql_models import Transcription, TranscriptionFeature, User, get_database_manager  # Temporarily disabled

logger = logging.getLogger(__name__)


class VoiceBridgeDataService:
    """Unified data service for VoiceBridge application"""

    def __init__(self, mysql_connection_string: str = None, mongodb_connection_string: str = None):
        """
        Initialize data service

        Args:
            mysql_connection_string: MySQL connection string
            mongodb_connection_string: MongoDB connection string
        """
        self.mysql_manager = get_database_manager(mysql_connection_string)
        self.mongodb_manager = get_mongodb_manager(mongodb_connection_string)

        self.mysql_connected = False
        self.mongodb_connected = False

    def connect_all(self) -> bool:
        """Connect to all databases"""
        try:
            # Connect to MySQL
            self.mysql_connected = self.mysql_manager.connect()
            if self.mysql_connected:
                self.mysql_manager.create_tables()

            # Connect to MongoDB
            self.mongodb_connected = self.mongodb_manager.connect()

            if self.mysql_connected and self.mongodb_connected:
                logger.info("All database connections established successfully")
                return True
            else:
                logger.warning("Some database connections failed")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            return False

    def close_all(self):
        """Close all database connections"""
        if self.mysql_connected:
            self.mysql_manager.close()
        if self.mongodb_connected:
            self.mongodb_manager.close()
        logger.info("All database connections closed")

    # User Management Methods
    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        first_name: str = None,
        last_name: str = None,
    ) -> Optional[int]:
        """Create a new user"""
        if not self.mysql_connected:
            logger.error("MySQL not connected")
            return None

        try:
            session = self.mysql_manager.get_session()
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            session.commit()
            user_id = user.id
            session.close()

            logger.info(f"User created successfully: {username} (ID: {user_id})")
            return int(user_id) if user_id is not None else None

        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None

    def get_user(self, user_id: int = None, username: str = None) -> Optional[Dict[str, Any]]:
        """Get user information"""
        if not self.mysql_connected:
            return None

        try:
            session = self.mysql_manager.get_session()
            if user_id:
                user = session.query(User).filter(User.id == user_id).first()
            elif username:
                user = session.query(User).filter(User.username == username).first()
            else:
                return None

            if user:
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "language_preference": user.language_preference,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                }
                session.close()
                return user_data
            else:
                session.close()
                return None

        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    # Transcription Management Methods
    def save_transcription(self, user_id: int, transcription_data: Dict[str, Any]) -> Optional[int]:
        """Save transcription to MySQL"""
        if not self.mysql_connected:
            logger.error("MySQL not connected")
            return None

        try:
            session = self.mysql_manager.get_session()

            # Create transcription record
            transcription = Transcription(
                user_id=user_id,
                session_id=transcription_data.get("session_id"),
                audio_file_path=transcription_data.get("audio_file_path"),
                audio_duration=transcription_data.get("audio_duration"),
                audio_size_bytes=transcription_data.get("audio_size_bytes"),
                sample_rate=transcription_data.get("sample_rate"),
                original_text=transcription_data.get("original_text"),
                processed_text=transcription_data.get("processed_text"),
                confidence_score=transcription_data.get("confidence_score"),
                language_detected=transcription_data.get("language_detected"),
                model_used=transcription_data.get("model_used"),
                preprocessing_used=transcription_data.get("preprocessing_used", False),
                processing_time=transcription_data.get("processing_time"),
            )

            session.add(transcription)
            session.commit()
            transcription_id = transcription.id

            # Save features if available
            if transcription_data.get("features"):
                features = TranscriptionFeature(
                    transcription_id=transcription_id,
                    mfcc_mean=json.dumps(transcription_data["features"].get("mfcc_mean", [])),
                    mfcc_std=json.dumps(transcription_data["features"].get("mfcc_std", [])),
                    mfcc_min=json.dumps(transcription_data["features"].get("mfcc_min", [])),
                    mfcc_max=json.dumps(transcription_data["features"].get("mfcc_max", [])),
                    spectral_centroid_mean=transcription_data["features"].get("spectral_centroid_mean"),
                    spectral_centroid_std=transcription_data["features"].get("spectral_centroid_std"),
                    spectral_rolloff_mean=transcription_data["features"].get("spectral_rolloff_mean"),
                    spectral_rolloff_std=transcription_data["features"].get("spectral_rolloff_std"),
                    spectral_bandwidth_mean=transcription_data["features"].get("spectral_bandwidth_mean"),
                    spectral_bandwidth_std=transcription_data["features"].get("spectral_bandwidth_std"),
                    zero_crossing_rate_mean=transcription_data["features"].get("zero_crossing_rate_mean"),
                    zero_crossing_rate_std=transcription_data["features"].get("zero_crossing_rate_std"),
                    chroma_mean=json.dumps(transcription_data["features"].get("chroma_mean", [])),
                    chroma_std=json.dumps(transcription_data["features"].get("chroma_std", [])),
                    tonnetz_mean=json.dumps(transcription_data["features"].get("tonnetz_mean", [])),
                    tonnetz_std=json.dumps(transcription_data["features"].get("tonnetz_std", [])),
                )
                session.add(features)
                session.commit()

            session.close()
            logger.info(f"Transcription saved successfully (ID: {transcription_id})")
            return int(transcription_id) if transcription_id is not None else None

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            return None

    def get_user_transcriptions(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's transcriptions"""
        if not self.mysql_connected:
            return []

        try:
            session = self.mysql_manager.get_session()
            transcriptions = (
                session.query(Transcription)
                .filter(Transcription.user_id == user_id)
                .order_by(Transcription.created_at.desc())
                .limit(limit)
                .all()
            )

            result = []
            for t in transcriptions:
                result.append(
                    {
                        "id": t.id,
                        "session_id": t.session_id,
                        "original_text": t.original_text,
                        "processed_text": t.processed_text,
                        "confidence_score": t.confidence_score,
                        "language_detected": t.language_detected,
                        "model_used": t.model_used,
                        "audio_duration": t.audio_duration,
                        "created_at": t.created_at,
                    }
                )

            session.close()
            return result

        except Exception as e:
            logger.error(f"Failed to get user transcriptions: {e}")
            return []

    # MongoDB Operations
    def create_conversation(self, user_id: str, session_id: str, title: str = None) -> Optional[str]:
        """Create a new conversation in MongoDB"""
        if not self.mongodb_connected:
            logger.error("MongoDB not connected")
            return None

        try:
            conversation = ConversationDocument.create_conversation(user_id=user_id, session_id=session_id, title=title)

            if self.mongodb_manager.db is not None:
                result = self.mongodb_manager.db.conversations.insert_one(conversation)
                conversation_id = str(result.inserted_id)
            else:
                logger.error("MongoDB database not available")
                return None

            logger.info(f"Conversation created successfully (ID: {conversation_id})")
            return conversation_id

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None

    def add_message_to_conversation(
        self,
        conversation_id: str,
        message_type: str,
        content: str,
        confidence: float = 0.0,
    ) -> bool:
        """Add message to conversation"""
        if not self.mongodb_connected:
            return False

        try:
            from bson import ObjectId

            if self.mongodb_manager.db is not None:
                conversation = self.mongodb_manager.db.conversations.find_one({"_id": ObjectId(conversation_id)})

                if conversation:
                    updated_conversation = ConversationDocument.add_message(
                        conversation, message_type, content, confidence
                    )

                    self.mongodb_manager.db.conversations.update_one(
                        {"_id": ObjectId(conversation_id)},
                        {"$set": updated_conversation},
                    )
                else:
                    logger.error(f"Conversation not found: {conversation_id}")
                    return False
            else:
                logger.error("MongoDB database not available")
                return False

                logger.info(f"Message added to conversation {conversation_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to add message to conversation: {e}")
            return False

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by ID"""
        if not self.mongodb_connected:
            return None

        try:
            from bson import ObjectId

            if self.mongodb_manager.db is not None:
                conversation = self.mongodb_manager.db.conversations.find_one({"_id": ObjectId(conversation_id)})

                if conversation:
                    # Convert ObjectId to string for JSON serialization
                    conversation["_id"] = str(conversation["_id"])
                    return conversation
                else:
                    return None
            else:
                logger.error("MongoDB database not available")
                return None
        except Exception as e:
            logger.error(f"Failed to get conversation: {e}")
            return None

    def save_audio_metadata(self, audio_metadata: Dict[str, Any]) -> bool:
        """Save audio metadata to MongoDB"""
        if not self.mongodb_connected:
            return False

        try:
            if self.mongodb_manager.db is not None:
                result = self.mongodb_manager.db.audio_metadata.insert_one(audio_metadata)
            else:
                logger.error("MongoDB database not available")
                return False
            logger.info(f"Audio metadata saved successfully (ID: {result.inserted_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to save audio metadata: {e}")
            return False

    # Analytics and Reporting
    def get_daily_analytics(self, date: str) -> Optional[Dict[str, Any]]:
        """Get daily analytics"""
        if not self.mongodb_connected:
            return None

        try:
            if self.mongodb_manager.db is not None:
                analytics = self.mongodb_manager.db.analytics.find_one({"_id": f"analytics_{date}"})

                if analytics:
                    analytics["_id"] = str(analytics["_id"])
                    return analytics
                else:
                    return None
            else:
                logger.error("MongoDB database not available")
                return None
        except Exception as e:
            logger.error(f"Failed to get daily analytics: {e}")
            return None

    def save_daily_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """Save daily analytics"""
        if not self.mongodb_connected:
            return False

        try:
            if self.mongodb_manager.db is not None:
                self.mongodb_manager.db.analytics.update_one(
                    {"_id": analytics_data["_id"]},
                    {"$set": analytics_data},
                    upsert=True,
                )
            else:
                logger.error("MongoDB database not available")
                return False
            logger.info(f"Daily analytics saved for {analytics_data.get('date')}")
            return True

        except Exception as e:
            logger.error(f"Failed to save daily analytics: {e}")
            return False


# Global data service instance
_data_service = None


def get_data_service(
    mysql_connection_string: str = None, mongodb_connection_string: str = None
) -> VoiceBridgeDataService:
    """Get data service instance"""
    global _data_service
    if _data_service is None:
        _data_service = VoiceBridgeDataService(mysql_connection_string, mongodb_connection_string)
    return _data_service
