# VoiceBridge API Postman Collection

This directory contains comprehensive Postman collections and environments for testing the VoiceBridge Real-time Speech-to-Text API.

## 📁 Files Overview

- `VoiceBridge_API_Collection.json` - Main API collection with all endpoints
- `VoiceBridge_Development_Environment.json` - Development environment variables
- `VoiceBridge_Production_Environment.json` - Production environment variables  
- `VoiceBridge_Testing_Environment.json` - Testing environment variables
- `README.md` - This documentation file

## 🚀 Quick Start

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button
3. Import the following files:
   - `VoiceBridge_API_Collection.json`
   - Choose one environment file based on your needs:
     - `VoiceBridge_Development_Environment.json` (for local development)
     - `VoiceBridge_Production_Environment.json` (for production)
     - `VoiceBridge_Testing_Environment.json` (for testing)

### 2. Configure Environment Variables

After importing, update the following environment variables with your actual values:

#### Required Variables:
- `openai_api_key` - Your OpenAI API key for Whisper service
- `jwt_secret_key` - JWT secret for token generation
- `encryption_key` - Encryption key for secure data storage

#### Optional Variables:
- `base_url` - API base URL (defaults provided)
- `test_username` - Test user credentials
- `test_email` - Test user email
- `test_password` - Test user password

### 3. Start Testing

1. Select the appropriate environment from the dropdown
2. Start with the **Authentication** folder
3. Register a new user or login with existing credentials
4. Tokens will be automatically saved to environment variables

## 📋 API Endpoints Overview

### 🔐 Authentication (`/auth`)
- **POST** `/auth/register` - Register new user
- **POST** `/auth/login` - User login
- **POST** `/auth/refresh` - Refresh access token
- **GET** `/auth/me` - Get current user info
- **PUT** `/auth/me` - Update user info
- **POST** `/auth/change-password` - Change password
- **POST** `/auth/logout` - Logout user
- **GET** `/auth/rate-limit-status` - Get rate limit status

### 🎤 Transcription (`/transcribe`)
- **POST** `/transcribe` - Transcribe audio file
- **GET** `/transcribe/{task_id}` - Get transcription result

### 🔄 Real-time Streaming (`/realtime`)
- **GET** `/realtime/status` - Get streaming service status
- **GET** `/realtime/sessions` - Get active sessions
- **GET** `/realtime/sessions/{session_id}` - Get session status
- **POST** `/realtime/sessions/{session_id}/broadcast` - Broadcast to session
- **GET** `/realtime/kafka/status` - Get Kafka status
- **GET** `/realtime/grpc/status` - Get gRPC status
- **POST** `/realtime/test/audio-stream` - Test audio streaming
- **GET** `/realtime/metrics` - Get real-time metrics
- **POST** `/realtime/cleanup/session/{session_id}` - Cleanup session

### 📊 Monitoring (`/monitoring`)
- **GET** `/monitoring/health` - System health check
- **GET** `/monitoring/metrics` - Prometheus metrics (text)
- **GET** `/monitoring/metrics/json` - Prometheus metrics (JSON)
- **GET** `/monitoring/mlflow/experiments` - MLFlow experiments
- **GET** `/monitoring/mlflow/performance-summary` - MLFlow performance
- **GET** `/monitoring/models/performance` - Model performance
- **GET** `/monitoring/models/alerts` - Model drift alerts
- **GET** `/monitoring/models/health` - Model health status
- **GET** `/monitoring/wandb/run-url` - W&B run URL
- **POST** `/monitoring/models/record-performance` - Record model metrics
- **GET** `/monitoring/system/resources` - System resources
- **GET** `/monitoring/logs/recent` - Recent logs
- **GET** `/monitoring/dashboard/summary` - Dashboard summary

### 🖥️ System (`/`)
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health check
- **POST** `/configure` - Configure API key

### 🔌 WebSocket Examples
- **WebSocket** `/ws/{client_id}` - Basic WebSocket connection
- **WebSocket** `/ws/{client_id}?token={token}` - Authenticated WebSocket
- **WebSocket** `/realtime/ws/stream` - Real-time streaming WebSocket

## 🔧 Environment Configurations

### Development Environment
- **Base URL**: `http://localhost:8000`
- **WebSocket URL**: `ws://localhost:8000`
- **Database**: Local MySQL/MongoDB instances
- **Services**: Local Redis, Kafka, MLFlow

### Production Environment
- **Base URL**: `https://api.voicebridge.com`
- **WebSocket URL**: `wss://api.voicebridge.com`
- **Database**: Production MySQL/MongoDB clusters
- **Services**: Production Redis, Kafka, MLFlow

### Testing Environment
- **Base URL**: `http://test-api.voicebridge.com`
- **WebSocket URL**: `ws://test-api.voicebridge.com`
- **Database**: Test MySQL/MongoDB instances
- **Services**: Test Redis, Kafka, MLFlow

## 🧪 Testing Workflows

### 1. Authentication Flow
```
1. Register User → 2. Login → 3. Get User Info → 4. Update User Info
```

### 2. Transcription Flow
```
1. Login → 2. Upload Audio File → 3. Get Transcription Result
```

### 3. Real-time Streaming Flow
```
1. Login → 2. Get Real-time Status → 3. Test Audio Stream → 4. Get Metrics
```

### 4. Monitoring Flow
```
1. Get System Health → 2. Get Metrics → 3. Check Model Performance → 4. View Dashboard
```

## 🔐 Authentication

Most endpoints require authentication using JWT tokens:

1. **Login** to get access and refresh tokens
2. Tokens are automatically saved to environment variables
3. Use `{{access_token}}` in Authorization header: `Bearer {{access_token}}`
4. **Refresh** tokens when they expire

## 📤 File Upload Testing

For audio file transcription:
1. Use the **Transcribe Audio File** request
2. In the Body tab, select **form-data**
3. Add key: `audio_file`, type: `File`
4. Select an audio file (WAV, MP3, M4A, etc.)

## 🔌 WebSocket Testing

WebSocket connections can be tested using:
1. **Postman WebSocket requests** (built-in support)
2. **External WebSocket clients** (like wscat)
3. **Browser WebSocket API**

Example WebSocket URL:
```
ws://localhost:8000/ws/test-client-123?token=your-access-token
```

## 📊 Monitoring and Metrics

The monitoring endpoints provide comprehensive system insights:

- **System Health**: Overall system status
- **Prometheus Metrics**: Performance metrics in text/JSON format
- **MLFlow Integration**: Experiment tracking and model performance
- **Model Monitoring**: Drift detection and performance alerts
- **W&B Integration**: Weights & Biases experiment tracking
- **System Resources**: CPU, memory, disk, network usage
- **Logs**: Recent application logs with filtering

## 🚨 Error Handling

The API returns standard HTTP status codes:
- **200**: Success
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **429**: Too Many Requests (rate limiting)
- **500**: Internal Server Error

## 🔄 Rate Limiting

The API implements rate limiting for:
- **Authentication endpoints**: 5 requests per minute
- **Transcription endpoints**: 10 requests per minute
- **WebSocket connections**: 3 connections per minute
- **General endpoints**: 100 requests per minute

Check rate limit status using: `GET /auth/rate-limit-status`

## 🛠️ Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Check if the API server is running
   - Verify the correct base URL in environment

2. **Authentication Errors**
   - Ensure valid API key is configured
   - Check if tokens are properly saved in environment

3. **File Upload Issues**
   - Verify file size is under limit (default: 25MB)
   - Check supported audio formats (WAV, MP3, M4A, etc.)

4. **WebSocket Connection Issues**
   - Ensure WebSocket URL is correct
   - Check if authentication token is valid

### Debug Tips:

1. **Check Environment Variables**: Ensure all required variables are set
2. **Review Response Headers**: Look for rate limiting and error information
3. **Monitor Console**: Check Postman console for detailed logs
4. **Test with curl**: Use curl commands for debugging

## 📚 Additional Resources

- [VoiceBridge API Documentation](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Postman Learning Center](https://learning.postman.com/)
- [WebSocket Testing Guide](https://learning.postman.com/docs/sending-requests/websocket/)

## 🤝 Contributing

To contribute to the Postman collection:

1. **Add New Endpoints**: Update the collection JSON file
2. **Update Environment Variables**: Add new variables as needed
3. **Improve Documentation**: Update this README with new features
4. **Test Thoroughly**: Ensure all requests work correctly

## 📝 Changelog

### Version 1.0.0
- Initial Postman collection with all API endpoints
- Development, Production, and Testing environments
- Comprehensive documentation
- Authentication flow automation
- WebSocket testing examples

---

**Note**: Remember to keep your API keys and secrets secure. Never commit sensitive information to version control.
