# Tests Directory

This directory contains the test suite for VoiceBridge application.

## Test Framework

The project uses **pytest** as the primary testing framework with the following structure:

- **pytest** - Main testing framework
- **unittest.mock** - Mocking and patching
- **requests** - HTTP API testing
- **websocket** - WebSocket connection testing

## Test Categories

### 🚀 **Core API Tests**
- `test_api.py` - Main API endpoint tests (health, root, WebSocket)
- `test_simple_api.py` - Simple API startup and basic functionality
- `test_simple_startup.py` - Application startup tests

### 🔒 **Security Tests**
- `test_security.py` - Authentication, authorization, and security features
- `test_mysql_passwords.py` - Database password security tests

### 📊 **Monitoring & ML Tests**
- `test_monitoring.py` - MLFlow, Prometheus, WandB monitoring tests
- `test_ml_models.py.skip` - Machine learning model tests (disabled)

### 🔄 **Real-time & Integration Tests**
- `test_realtime.py` - Real-time WebSocket and streaming tests
- `test_database_integration.py.skip` - Database integration tests (disabled)
- `test_data_processing_systems.py.skip` - Data processing tests (disabled)

### 🛠️ **Utility Tests**
- `test_fixes.py` - Bug fixes and regression tests

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest requests websocket-client

# Ensure the application is running
python main.py
```

### Test Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src

# Run only non-skipped tests
pytest -m "not skip"

# Run tests in parallel
pytest -n auto
```

### Test Configuration
Tests are configured to:
- Use `unittest.mock` for mocking external services
- Test both success and failure scenarios
- Include WebSocket connection tests
- Mock MLFlow and monitoring services for isolated testing

## Test Structure

### API Tests
```python
def test_health_endpoint():
    """Test the health check endpoint."""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
```

### WebSocket Tests
```python
def test_websocket_connection():
    """Test WebSocket connection."""
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:8000/ws")
    # Test WebSocket functionality
```

### Mock Tests
```python
@patch('src.services.mlflow_service.mlflow_service')
def test_mlflow_service(mock_mlflow):
    """Test MLFlow service with mocking."""
    mock_mlflow.return_value = Mock()
    # Test with mocked service
```

## Skipped Tests

Some tests are marked with `.skip` extension and are disabled by default:
- `test_ml_models.py.skip` - Requires ML model files
- `test_database_integration.py.skip` - Requires database setup
- `test_data_processing_systems.py.skip` - Requires Spark/Hadoop setup

To enable these tests:
1. Remove the `.skip` extension
2. Ensure required dependencies are installed
3. Configure necessary services (database, Spark, etc.)

## Continuous Integration

Tests are integrated into the CI/CD pipeline:
- Pre-commit hooks run basic tests
- GitHub Actions runs full test suite
- Coverage reports are generated
- Test results are published

## Troubleshooting

### Common Issues
- **Connection refused**: Ensure the API is running on localhost:8000
- **Import errors**: Check that all dependencies are installed
- **WebSocket errors**: Verify WebSocket server is running
- **Mock failures**: Check mock configurations and patches

### Debug Mode
```bash
# Run tests with debug output
pytest -s -v

# Run single test with debug
pytest tests/test_api.py::test_health_endpoint -s -v
```
