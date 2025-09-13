# Configuration Guide

## Environment Variables

### Required Configuration

#### OpenAI API Key
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
**Purpose**: Required for AI transcription functionality
**How to get**: Sign up at https://platform.openai.com/api-keys

### Server Configuration

#### Basic Server Settings
```bash
# Server host and port
HOST=127.0.0.1
PORT=8000

# Environment
NODE_ENV=development
VITE_API_URL=http://localhost:8000
```

#### CORS Settings
```bash
# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Database Configuration

#### MySQL Database
```bash
DATABASE_URL=mysql://username:password@localhost:3306/voicebridge
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=voicebridge
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=voicebridge
```

#### MongoDB Database
```bash
MONGODB_URL=mongodb://localhost:27017/voicebridge
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=voicebridge
```

#### Redis Cache
```bash
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

### Authentication Configuration

#### JWT Settings
```bash
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### OAuth2 Configuration
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

### Message Queue Configuration

#### Kafka Settings
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_AUDIO=audio_streams
KAFKA_TOPIC_TRANSCRIPTION=transcriptions
KAFKA_GROUP_ID=voicebridge_group
```

#### Celery Settings
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
```

### ML Services Configuration

#### MLflow Settings
```bash
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=voicebridge_experiments
MLFLOW_ARTIFACT_ROOT=./mlflow_artifacts
```

#### Weights & Biases
```bash
WANDB_API_KEY=your_wandb_api_key
WANDB_PROJECT=voicebridge
WANDB_ENTITY=your_username
```

#### Model Configuration
```bash
# Default model settings
DEFAULT_MODEL=whisper
DEFAULT_LANGUAGE=en
MAX_AUDIO_SIZE_MB=25
SUPPORTED_AUDIO_FORMATS=wav,mp3,m4a,flac,webm,ogg

# Model performance settings
MODEL_CACHE_SIZE=100
MODEL_TIMEOUT_SECONDS=30
```

### Monitoring Configuration

#### Prometheus Settings
```bash
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PATH=/metrics
PROMETHEUS_SCRAPE_INTERVAL=15s
```

#### Grafana Settings
```bash
GRAFANA_PORT=3001
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin_password
```

### Security Configuration

#### Encryption Settings
```bash
ENCRYPTION_KEY=your_32_character_encryption_key
ENCRYPTION_ALGORITHM=AES-256-GCM
```

#### Rate Limiting
```bash
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST_SIZE=10
RATE_LIMIT_WINDOW_SECONDS=60
```

#### Security Headers
```bash
SECURITY_HEADERS_ENABLED=true
CSP_POLICY=default-src 'self'
HSTS_ENABLED=true
```

### File Storage Configuration

#### Local Storage
```bash
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=audio/*
```

#### Cloud Storage (Optional)
```bash
# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=voicebridge-storage
AWS_REGION=us-east-1

# Google Cloud Storage
GCS_BUCKET_NAME=voicebridge-storage
GCS_CREDENTIALS_PATH=./credentials/gcs.json

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT=your_storage_account
AZURE_STORAGE_KEY=your_storage_key
AZURE_CONTAINER_NAME=voicebridge
```

### Logging Configuration

#### Log Levels
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=./logs/voicebridge.log
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5
```

#### Structured Logging
```bash
STRUCTURED_LOGGING=true
LOG_CORRELATION_ID=true
LOG_USER_ID=true
```

### Performance Configuration

#### Caching Settings
```bash
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE_MB=100
CACHE_STRATEGY=LRU
```

#### Connection Pooling
```bash
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

#### Async Settings
```bash
ASYNC_WORKERS=4
ASYNC_MAX_CONNECTIONS=100
ASYNC_KEEPALIVE_TIMEOUT=5
```

## Configuration Files

### .env File Template
```bash
# Copy this to .env and fill in your values
cp .env.example .env
```

### Docker Environment
```bash
# For Docker deployment
cp .env.docker .env
```

### Production Environment
```bash
# For production deployment
cp .env.production .env
```

## Validation

### Configuration Validation
```bash
# Validate configuration
python scripts/validate_config.py

# Test database connections
python scripts/test_connections.py
```

### Health Checks
```bash
# Check all services
make health

# Check specific service
curl http://localhost:8000/health
```

## Security Best Practices

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords and API keys
- Rotate secrets regularly
- Use environment-specific configurations

### Database Security
- Use strong passwords
- Enable SSL/TLS connections
- Restrict network access
- Regular backups

### API Security
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Monitor for suspicious activity

## Troubleshooting

### Common Configuration Issues
1. **Missing API keys**: Check OpenAI API key validity
2. **Database connection**: Verify connection strings and credentials
3. **Port conflicts**: Ensure ports are available
4. **File permissions**: Check upload directory permissions

### Configuration Testing
```bash
# Test configuration
python -c "from config import settings; print('Config loaded successfully')"

# Test database connection
python scripts/test_db_connection.py

# Test external services
python scripts/test_external_services.py
```
