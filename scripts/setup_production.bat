@echo off
echo Setting up VoiceBridge for Production...

REM Create .env file
echo Creating production .env file...
(
echo # VoiceBridge Production Environment Configuration
echo # Generated for production setup
echo.
echo # Database Configuration
echo MYSQL_CONNECTION_STRING=mysql+mysqlconnector://root:voicebridge123@localhost:3306/voicebridge
echo MONGODB_CONNECTION_STRING=mongodb://localhost:27017/voicebridge
echo.
echo # Redis Configuration
echo REDIS_URL=redis://localhost:6379/0
echo.
echo # Security Configuration
echo SECRET_KEY=voicebridge-super-secret-production-key-2024-min-32-chars-long
echo ENCRYPTION_KEY=voicebridge-32-byte-encryption-key-12345678901234567890123456789012
echo.
echo # JWT Configuration
echo ACCESS_TOKEN_EXPIRE_MINUTES=30
echo REFRESH_TOKEN_EXPIRE_DAYS=7
echo ALGORITHM=HS256
echo.
echo # Rate Limiting Configuration
echo RATE_LIMIT_REQUESTS=100
echo RATE_LIMIT_WINDOW=60
echo.
echo # API Configuration
echo API_HOST=0.0.0.0
echo API_PORT=8000
echo API_DEBUG=False
echo.
echo # OpenAI Configuration
echo # Replace with your actual OpenAI API key
echo OPENAI_API_KEY=sk-your-openai-api-key-here
echo.
echo # Audio Processing Configuration
echo MAX_AUDIO_SIZE_MB=10
echo SUPPORTED_AUDIO_FORMATS=wav,mp3,m4a,flac,webm
echo SAMPLE_RATE=16000
echo DEFAULT_LANGUAGE=en
echo.
echo # Kafka Configuration
echo KAFKA_BOOTSTRAP_SERVERS=localhost:9092
echo KAFKA_AUDIO_TOPIC=voicebridge-audio
echo KAFKA_TRANSCRIPTION_TOPIC=voicebridge-transcription
echo.
echo # gRPC Configuration
echo GRPC_PORT=50051
echo GRPC_MAX_WORKERS=10
echo.
echo # Celery Configuration
echo CELERY_BROKER_URL=redis://localhost:6379/0
echo CELERY_RESULT_BACKEND=redis://localhost:6379/0
echo.
echo # MLFlow Configuration
echo MLFLOW_TRACKING_URI=http://localhost:5000
echo MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
echo MLFLOW_DEFAULT_ARTIFACT_ROOT=./mlflow_artifacts
echo.
echo # Weights & Biases Configuration
echo # Replace with your actual W&B API key
echo WANDB_API_KEY=your-wandb-api-key-here
echo WANDB_ENTITY=your-wandb-entity
echo WANDB_PROJECT=voicebridge-speech-recognition
echo.
echo # Monitoring Configuration
echo PROMETHEUS_METRICS_ENABLED=true
echo GRAFANA_DASHBOARD_URL=http://localhost:3001
echo MLFLOW_UI_URL=http://localhost:5000
echo.
echo # Production Settings
echo NODE_ENV=production
echo VITE_API_URL=http://localhost:8000
) > .env

echo .env file created successfully!
echo.
echo IMPORTANT: Please update the following in .env file:
echo 1. OPENAI_API_KEY - Add your OpenAI API key
echo 2. WANDB_API_KEY - Add your Weights & Biases API key (optional)
echo 3. Database passwords if different
echo.
echo Next steps:
echo 1. Run: scripts\setup_redis.bat
echo 2. Run: scripts\setup_mlflow.bat
echo 3. Run: scripts\setup_kafka.bat
echo 4. Update .env with your API keys
echo 5. Run: python main.py
