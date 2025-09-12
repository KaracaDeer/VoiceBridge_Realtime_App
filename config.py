"""
Configuration settings for the VoiceBridge real-time speech-to-text application.

This module contains all application settings loaded from environment variables.
Users can customize the application behavior by setting these environment variables
or creating a .env file in the project root.

Key configuration areas:
- API and server settings
- Database connections (Redis, MySQL, MongoDB)
- ML services (OpenAI, MLflow, Weights & Biases)
- Audio processing parameters
- Security and authentication settings
- Monitoring and logging configuration
"""
import os
from typing import Any

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file (optional)
load_dotenv()  # Enable .env file loading


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden by setting corresponding environment variables.
    For example: export OPENAI_API_KEY="your-key-here"
    """

    # Redis Configuration - Used for caching and rate limiting
    redis_url: str = "redis://localhost:6379/0"

    # Kafka Configuration - For real-time audio streaming and message queuing
    # (Defined later with environment variable support)

    # Celery Configuration - Background task processing (using in-memory for testing)
    celery_broker_url: str = "memory://"
    celery_result_backend: str = "cache+memory://"

    # API Configuration - Server host, port, and debug settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # Audio Processing Configuration - File size limits and supported formats
    max_audio_size_mb: int = 10
    supported_audio_formats: str = "wav,mp3,m4a,flac,webm"
    sample_rate: int = 16000  # Standard sample rate for speech recognition

    # OpenAI Configuration - API key and language settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")  # Set in .env file
    default_language: str = "en"  # Default language for transcription

    # Weights & Biases Configuration
    wandb_api_key: str = os.getenv("WANDB_API_KEY", "")
    wandb_project: str = os.getenv("WANDB_PROJECT", "voicebridge")

    # MLFlow Configuration
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate Limiting Configuration
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Encryption Configuration
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "your-32-byte-encryption-key-here")

    # Database Configuration
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_connection_string: str = os.getenv(
        "MYSQL_CONNECTION_STRING", f"mysql+mysqlconnector://root:{mysql_password}@localhost:3306/voicebridge"
    )
    mongodb_connection_string: str = os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")

    # Database Demo Mode (when MySQL is not available)
    database_demo_mode: bool = os.getenv("DATABASE_DEMO_MODE", "true").lower() == "true"

    # Kafka Configuration
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_audio_topic: str = os.getenv("KAFKA_AUDIO_TOPIC", "voicebridge-audio")
    kafka_transcription_topic: str = os.getenv("KAFKA_TRANSCRIPTION_TOPIC", "voicebridge-transcription")

    def model_post_init(self, __context: Any) -> None:
        # If a password is provided via .env, ensure the connection string includes it
        try:
            if self.mysql_password:
                if "mysql+mysqlconnector://" in self.mysql_connection_string:
                    # Inject password if missing (e.g., root:@localhost → root:PWD@localhost)
                    if ":@" in self.mysql_connection_string:
                        self.mysql_connection_string = self.mysql_connection_string.replace(
                            ":@", f":{self.mysql_password}@"
                        )
                    # Or if no credentials present at all (unlikely given defaults)
                    elif "//root@" in self.mysql_connection_string:
                        self.mysql_connection_string = self.mysql_connection_string.replace(
                            "//root@", f"//root:{self.mysql_password}@"
                        )
        except Exception:
            # Do not fail settings initialization on formatting errors
            pass

    # gRPC Configuration
    grpc_port: int = int(os.getenv("GRPC_PORT", "50051"))
    grpc_max_workers: int = int(os.getenv("GRPC_MAX_WORKERS", "10"))

    class Config:
        # env_file = ".env"  # Commented out to avoid .env dependency
        case_sensitive = False


# Global settings instance
settings = Settings()
