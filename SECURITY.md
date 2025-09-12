# VoiceBridge Security Documentation

## Overview

VoiceBridge implements comprehensive security measures to protect user data, audio files, and API endpoints. This document outlines the security features and best practices implemented in the system.

## Security Features

### 1. Authentication & Authorization

#### JWT Token-Based Authentication
- **Access Tokens**: Short-lived tokens (30 minutes) for API access
- **Refresh Tokens**: Long-lived tokens (7 days) for token renewal
- **Token Security**: Signed with HS256 algorithm using secret key
- **User Management**: Complete user registration, login, and profile management

#### Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile
- `POST /auth/change-password` - Change password
- `POST /auth/logout` - User logout

### 2. Rate Limiting

#### FastAPI-Limiter Integration
- **Transcription Endpoints**: 10 requests per minute
- **WebSocket Connections**: 5 connections per minute
- **Authentication**: 5 attempts per 5 minutes
- **General API**: 100 requests per minute (configurable)

#### Redis-Based Distributed Rate Limiting
- Centralized rate limiting across multiple server instances
- IP-based and user-based rate limiting
- Automatic cleanup of expired rate limit entries

### 3. Audio File Encryption

#### AES-256 Encryption
- **Algorithm**: AES-256 with Fernet encryption
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Salt**: Unique salt per encryption (configurable)
- **Storage**: Encrypted audio files stored securely

#### Secure Storage Service
- Encrypted file storage with metadata
- User-based access control
- File integrity verification
- Automatic cleanup of expired files

### 4. Security Headers

#### HTTP Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy`: Comprehensive CSP policy

### 5. Request Logging & Monitoring

#### Security Event Logging
- Authentication attempts and failures
- Rate limit violations
- Suspicious request patterns
- Unauthorized access attempts
- Server errors and exceptions

#### Request Tracking
- Processing time monitoring
- IP address tracking
- User agent logging
- Request/response correlation

## Configuration

### Environment Variables

```bash
# Security Configuration
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ENCRYPTION_KEY=your-32-byte-encryption-key-here-12345678901234567890123456789012

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Database
MYSQL_CONNECTION_STRING=mysql+mysqlconnector://root:password@localhost:3306/voicebridge
REDIS_URL=redis://localhost:6379/0
```

### Security Best Practices

#### 1. Secret Key Management
- Use strong, randomly generated secret keys
- Store keys in environment variables, not in code
- Rotate keys regularly in production
- Use different keys for different environments

#### 2. Database Security
- Use strong database passwords
- Enable SSL/TLS for database connections
- Regular database backups
- Implement database access controls

#### 3. Network Security
- Use HTTPS in production
- Implement proper CORS policies
- Use reverse proxy (nginx) for additional security
- Consider IP whitelisting for admin endpoints

#### 4. File Storage Security
- Encrypt all sensitive files
- Implement proper file access controls
- Regular security audits of stored files
- Secure file deletion procedures

## API Security

### Authentication Flow

1. **User Registration**
   ```bash
   POST /auth/register
   {
     "username": "user123",
     "email": "user@example.com",
     "password": "securepassword123"
   }
   ```

2. **User Login**
   ```bash
   POST /auth/login
   {
     "username": "user123",
     "password": "securepassword123"
   }
   ```

3. **Using Access Token**
   ```bash
   GET /transcribe
   Authorization: Bearer <access_token>
   ```

### Rate Limiting Headers

The API includes rate limiting information in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Error Handling

Security-related errors return appropriate HTTP status codes:

- `401 Unauthorized`: Invalid or missing authentication
- `403 Forbidden`: Insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded
- `400 Bad Request`: Invalid request data

## WebSocket Security

### Authentication
- Optional token-based authentication for WebSocket connections
- Rate limiting for WebSocket connections
- Encrypted audio data transmission

### Usage
```javascript
// Connect with authentication
const ws = new WebSocket('ws://localhost:8000/ws/client123?token=<access_token>');

// Connect without authentication (limited functionality)
const ws = new WebSocket('ws://localhost:8000/ws/client123');
```

## Monitoring & Alerting

### Security Metrics
- Failed authentication attempts
- Rate limit violations
- Unusual request patterns
- File access patterns
- System resource usage

### Log Analysis
- Centralized logging with structured format
- Real-time security event monitoring
- Automated alerting for security incidents
- Regular security audit reports

## Compliance

### Data Protection
- Audio files encrypted at rest
- Secure transmission protocols
- User data anonymization options
- Data retention policies

### Privacy
- Minimal data collection
- User consent management
- Data deletion capabilities
- Privacy policy compliance

## Security Updates

### Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Regular security assessments
- Penetration testing

### Incident Response
- Security incident response plan
- Data breach notification procedures
- Recovery and remediation processes
- Post-incident analysis

## Contact

For security-related questions or to report security vulnerabilities, please contact the development team.

## Changelog

- **v1.0.0**: Initial security implementation
  - JWT authentication
  - Rate limiting
  - AES-256 encryption
  - Security headers
  - Request logging
