"""
MySQL Database Models for VoiceBridge
Structured data storage for users, transcriptions, and system logs
"""
import logging
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class User(Base):
    """User model for storing user information"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_preference = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transcriptions = relationship("Transcription", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")


class Transcription(Base):
    """Transcription model for storing speech-to-text results"""

    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=True)

    # Audio information
    audio_file_path = Column(String(500))
    audio_duration = Column(Float)
    audio_size_bytes = Column(Integer)
    sample_rate = Column(Integer)

    # Transcription results
    original_text = Column(Text)
    processed_text = Column(Text)
    confidence_score = Column(Float)
    language_detected = Column(String(10))

    # ML model information
    model_used = Column(String(100))
    preprocessing_used = Column(Boolean, default=False)
    processing_time = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transcriptions")
    features = relationship("TranscriptionFeature", back_populates="transcription")


class TranscriptionFeature(Base):
    """Transcription features extracted during preprocessing"""

    __tablename__ = "transcription_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=False)

    # MFCC features
    mfcc_mean = Column(Text)  # JSON string of array
    mfcc_std = Column(Text)
    mfcc_min = Column(Text)
    mfcc_max = Column(Text)

    # Spectral features
    spectral_centroid_mean = Column(Float)
    spectral_centroid_std = Column(Float)
    spectral_rolloff_mean = Column(Float)
    spectral_rolloff_std = Column(Float)
    spectral_bandwidth_mean = Column(Float)
    spectral_bandwidth_std = Column(Float)
    zero_crossing_rate_mean = Column(Float)
    zero_crossing_rate_std = Column(Float)

    # Chroma and Tonnetz features
    chroma_mean = Column(Text)  # JSON string of array
    chroma_std = Column(Text)
    tonnetz_mean = Column(Text)  # JSON string of array
    tonnetz_std = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transcription = relationship("Transcription", back_populates="features")


class UserSession(Base):
    """User session tracking"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), unique=True, nullable=False)

    # Session information
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_type = Column(String(50))

    # Session metrics
    total_transcriptions = Column(Integer, default=0)
    total_audio_duration = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    last_activity = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")


class SystemLog(Base):
    """System logs and monitoring data"""

    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Log information
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(100), nullable=False)  # ML, API, Database, etc.
    message = Column(Text, nullable=False)

    # Context
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    request_id = Column(String(100), nullable=True)

    # Performance metrics
    processing_time = Column(Float)
    memory_usage = Column(Float)
    cpu_usage = Column(Float)

    # Additional data
    additional_data = Column(Text)  # JSON string for additional context

    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """MySQL database manager"""

    def __init__(self, connection_string: str):
        """
        Initialize database manager

        Args:
            connection_string: MySQL connection string
        """
        self.connection_string = connection_string
        self.engine = None
        self.SessionLocal = None

    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.engine = create_engine(
                self.connection_string,
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True,
                pool_recycle=300,
            )

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            logger.info("MySQL database connection established")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MySQL database: {e}")
            return False

    def create_tables(self) -> bool:
        """Create all database tables"""
        try:
            if self.engine is None:
                logger.error("Database engine not initialized")
                return False
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            return False

    def get_session(self):
        """Get database session"""
        if self.SessionLocal is None:
            raise Exception("Database not connected. Call connect() first.")
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("MySQL database connection closed")


# Global database manager instance
_db_manager = None


def get_database_manager(connection_string: str = None) -> DatabaseManager:
    """Get database manager instance"""
    global _db_manager
    if _db_manager is None:
        if connection_string is None:
            # Default connection string for local MySQL
            connection_string = "mysql+mysqlconnector://root:password@localhost:3306/voicebridge"
        _db_manager = DatabaseManager(connection_string)
    return _db_manager
