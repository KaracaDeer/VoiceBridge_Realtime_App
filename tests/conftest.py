"""
Pytest configuration and fixtures for VoiceBridge API tests.
Provides common fixtures and test utilities.
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)


@pytest.fixture
def mock_whisper_service():
    """Mock OpenAI Whisper service."""
    with patch('main.whisper_service') as mock:
        mock.transcribe_audio_bytes = Mock()
        mock.is_api_available.return_value = True
        mock.get_service_info.return_value = {
            "provider": "openai",
            "model": "whisper-1",
            "available": True
        }
        yield mock


@pytest.fixture
def mock_rate_limiting_service():
    """Mock rate limiting service."""
    with patch('main.rate_limiting_service') as mock:
        mock.get_client_identifier.return_value = "test_client"
        mock.enforce_rate_limit.return_value = None
        yield mock


@pytest.fixture
def mock_monitoring_services():
    """Mock all monitoring services."""
    with patch('main.model_monitoring_service') as mock_monitoring, \
         patch('main.mlflow_service') as mock_mlflow, \
         patch('main.wandb_service') as mock_wandb, \
         patch('main.prometheus_metrics') as mock_prometheus:
        
        # Configure monitoring mocks
        mock_monitoring.record_model_performance.return_value = None
        mock_mlflow.log_transcription_metrics.return_value = None
        mock_wandb.log_transcription_metrics.return_value = None
        mock_prometheus.record_transcription.return_value = None
        
        yield {
            "monitoring": mock_monitoring,
            "mlflow": mock_mlflow,
            "wandb": mock_wandb,
            "prometheus": mock_prometheus
        }


@pytest.fixture
def mock_encryption_service():
    """Mock encryption service."""
    with patch('main.encryption_service') as mock:
        mock.encrypt_audio_file.return_value = (b"encrypted_data", {"key": "test_key"})
        mock.get_encryption_info.return_value = {
            "algorithm": "AES-256",
            "status": "active"
        }
        yield mock


@pytest.fixture
def mock_audio_processor():
    """Mock audio processor service."""
    with patch('main.audio_processor') as mock:
        mock.is_valid_audio_format.return_value = True
        yield mock


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.id = 123
    user.username = "test_user"
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_audio_data():
    """Sample audio data for testing."""
    return b"fake_audio_data_for_testing_purposes"


@pytest.fixture
def sample_transcription_result():
    """Sample transcription result."""
    return {
        "text": "This is a test transcription",
        "confidence": 0.95,
        "language": "en",
        "provider": "openai"
    }


@pytest.fixture
def temp_audio_file(sample_audio_data):
    """Create temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(sample_audio_data)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mock_all_services():
    """Mock all external services for comprehensive testing."""
    with patch('main.whisper_service') as mock_whisper, \
         patch('main.rate_limiting_service') as mock_rate_limit, \
         patch('main.model_monitoring_service') as mock_monitoring, \
         patch('main.mlflow_service') as mock_mlflow, \
         patch('main.wandb_service') as mock_wandb, \
         patch('main.prometheus_metrics') as mock_prometheus, \
         patch('main.encryption_service') as mock_encryption, \
         patch('main.audio_processor') as mock_processor:
        
        # Configure all mocks
        mock_whisper.transcribe_audio_bytes.return_value = {
            "text": "Mock transcription",
            "confidence": 0.9,
            "language": "en",
            "provider": "openai"
        }
        mock_whisper.is_api_available.return_value = True
        mock_whisper.get_service_info.return_value = {
            "provider": "openai",
            "model": "whisper-1",
            "available": True
        }
        
        mock_rate_limit.get_client_identifier.return_value = "test_client"
        mock_rate_limit.enforce_rate_limit.return_value = None
        
        mock_encryption.encrypt_audio_file.return_value = (b"encrypted_data", {"key": "test_key"})
        mock_processor.is_valid_audio_format.return_value = True
        
        yield {
            "whisper": mock_whisper,
            "rate_limit": mock_rate_limit,
            "monitoring": mock_monitoring,
            "mlflow": mock_mlflow,
            "wandb": mock_wandb,
            "prometheus": mock_prometheus,
            "encryption": mock_encryption,
            "processor": mock_processor
        }


@pytest.fixture
def websocket_client():
    """Mock WebSocket client for testing."""
    return Mock()


@pytest.fixture
def mock_kafka_services():
    """Mock Kafka services."""
    with patch('main.kafka_producer') as mock_producer, \
         patch('main.kafka_consumer') as mock_consumer, \
         patch('main.kafka_stream_service') as mock_stream:
        
        mock_producer.send_audio.return_value = None
        mock_producer.send_audio_stream.return_value = None
        mock_consumer.is_connected.return_value = True
        mock_stream.start.return_value = True
        mock_stream.stop.return_value = None
        
        yield {
            "producer": mock_producer,
            "consumer": mock_consumer,
            "stream": mock_stream
        }


@pytest.fixture
def mock_grpc_service():
    """Mock gRPC service."""
    with patch('main.grpc_server') as mock_grpc:
        mock_grpc.start.return_value = True
        mock_grpc.stop.return_value = None
        yield mock_grpc


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "websocket: WebSocket tests")
    config.addinivalue_line("markers", "ml: Machine learning tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_api: Tests that require external API keys")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_websocket" in item.nodeid:
            item.add_marker(pytest.mark.websocket)
        elif "test_ml" in item.nodeid:
            item.add_marker(pytest.mark.ml)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# Test reporting
def pytest_html_report_title(report):
    """Set HTML report title."""
    report.title = "VoiceBridge API Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Customize HTML report summary."""
    prefix.extend([f"<p>VoiceBridge Real-time Speech-to-Text API Test Results</p>"])
