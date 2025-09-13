# Test Documentation

## Test Overview

VoiceBridge includes comprehensive testing coverage for all major components:

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: End-to-end functionality
- **WebSocket Tests**: Real-time streaming functionality
- **ML Model Tests**: AI/ML model performance and accuracy
- **API Tests**: REST API endpoints and responses

## Test Structure

```
tests/
├── conftest.py              # Test fixtures and configuration
├── test_api.py              # API endpoint tests
├── test_websocket_stream.py # WebSocket streaming tests
├── test_ml_models.py        # ML model tests
├── test_integration.py      # Integration tests
├── test_security.py         # Security tests
├── test_realtime.py         # Real-time functionality tests
└── README.md               # This file
```

## Running Tests

### Quick Test Commands
```bash
# Run all tests
make test

# Run Python tests only
make test-python

# Run frontend tests only
make test-frontend

# Run with coverage
make test-coverage
```

### Detailed Test Commands
```bash
# Run specific test file
pytest tests/test_api.py

# Run tests with verbose output
pytest -v

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel
pytest -n auto

# Run only failed tests
pytest --lf
```

### Test Categories
```bash
# Run unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run WebSocket tests
pytest -m websocket

# Run ML tests
pytest -m ml

# Run API tests
pytest -m api
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    websocket: WebSocket tests
    ml: Machine learning tests
    api: API endpoint tests
```

### Test Fixtures (conftest.py)
- `client`: FastAPI test client
- `mock_whisper_service`: Mocked OpenAI Whisper service
- `mock_rate_limiting_service`: Mocked rate limiting
- `mock_monitoring_services`: Mocked monitoring services
- `sample_audio_data`: Test audio data
- `sample_transcription_result`: Expected transcription results

## Test Types

### 1. API Tests (test_api.py)
Tests REST API endpoints:
- Health check endpoints
- Authentication endpoints
- Transcription endpoints
- Error handling
- Response formats

**Example:**
```python
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 2. WebSocket Tests (test_websocket_stream.py)
Tests real-time streaming:
- WebSocket connection establishment
- Audio data streaming
- Real-time transcription
- Connection management
- Error handling

**Example:**
```python
async def test_websocket_connection_success(mock_whisper_service):
    async with websockets.connect("ws://localhost:8000/ws/test_client") as websocket:
        await websocket.send(b"fake_audio_data")
        response = await websocket.recv()
        assert "acknowledgment" in response
```

### 3. ML Model Tests (test_ml_models.py)
Tests AI/ML functionality:
- Model performance metrics
- Transcription accuracy
- Confidence scoring
- Error handling
- Model switching

**Example:**
```python
def test_whisper_transcription_success(mock_whisper_service):
    result = whisper_service.transcribe_audio_bytes(b"test_audio")
    assert result["text"] == "test transcription"
    assert result["confidence"] > 0.8
```

### 4. Integration Tests (test_integration.py)
Tests end-to-end functionality:
- Complete user workflows
- Service integration
- System behavior
- Performance under load
- Error recovery

**Example:**
```python
def test_complete_transcription_workflow(client, mock_services):
    # Upload audio file
    response = client.post("/transcribe", files={"audio_file": ("test.wav", b"audio_data")})
    assert response.status_code == 200
    
    # Verify transcription result
    result = response.json()
    assert "transcription" in result
    assert result["confidence"] > 0.8
```

### 5. Security Tests (test_security.py)
Tests security features:
- Authentication mechanisms
- Authorization checks
- Input validation
- Rate limiting
- Encryption

**Example:**
```python
def test_rate_limiting(client):
    # Send multiple requests quickly
    for _ in range(100):
        response = client.get("/health")
    
    # Should be rate limited
    assert response.status_code == 429
```

## Test Data

### Sample Audio Data
```python
# Test audio files (synthetic)
sample_audio_data = b"fake_audio_data_for_testing"

# Expected transcription results
sample_transcription_result = {
    "text": "This is a test transcription",
    "confidence": 0.95,
    "language": "en",
    "provider": "openai"
}
```

### Mock Services
All external services are mocked for testing:
- OpenAI Whisper API
- Database connections
- Redis cache
- Kafka messaging
- MLflow tracking

## Test Coverage

### Coverage Goals
- **Overall Coverage**: 85%+
- **API Endpoints**: 90%+
- **Core Services**: 90%+
- **ML Models**: 80%+
- **WebSocket**: 85%+

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html

# Generate coverage badge
coverage-badge -o coverage.svg
```

## Continuous Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled runs

### Local CI
```bash
# Run local CI pipeline
make ci

# Run CI tests
make ci-test
```

## Test Best Practices

### Writing Tests
1. **Test one thing at a time**
2. **Use descriptive test names**
3. **Mock external dependencies**
4. **Test both success and failure cases**
5. **Keep tests independent**

### Test Organization
1. **Group related tests in classes**
2. **Use fixtures for common setup**
3. **Mark tests with appropriate categories**
4. **Keep test data minimal and focused**

### Performance Testing
```bash
# Run performance tests
pytest tests/test_performance.py

# Load testing
pytest tests/test_load.py -v
```

## Debugging Tests

### Verbose Output
```bash
# Run with verbose output
pytest -v -s

# Show print statements
pytest -s

# Show local variables on failure
pytest --tb=long
```

### Debugging Specific Tests
```bash
# Run single test with debugging
pytest tests/test_api.py::test_health_endpoint -v -s

# Drop into debugger on failure
pytest --pdb

# Run with coverage and debugging
pytest --cov=src --pdb
```

## Test Maintenance

### Updating Tests
1. **Update tests when changing functionality**
2. **Remove obsolete tests**
3. **Keep test data current**
4. **Update mocks when APIs change**

### Test Performance
1. **Run tests regularly**
2. **Monitor test execution time**
3. **Optimize slow tests**
4. **Use parallel execution where possible**

## Troubleshooting

### Common Issues
1. **Import errors**: Check Python path and dependencies
2. **Mock failures**: Verify mock configurations
3. **Timeout errors**: Increase timeout values
4. **Database errors**: Check test database setup

### Test Environment
```bash
# Check test environment
python -c "import pytest; print('pytest available')"

# Verify test dependencies
pip install -r requirements-test.txt

# Check test configuration
pytest --collect-only
```