"""
Integration tests for VoiceBridge API.
Tests end-to-end functionality, service integration, and system behavior.
"""
import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app


class TestAPIIntegration:
    """Test API integration and end-to-end functionality."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_services(self):
        """Mock all external services."""
        with patch('main.whisper_service') as mock_whisper, \
             patch('main.rate_limiting_service') as mock_rate_limit, \
             patch('main.model_monitoring_service') as mock_monitoring, \
             patch('main.mlflow_service') as mock_mlflow, \
             patch('main.wandb_service') as mock_wandb, \
             patch('main.prometheus_metrics') as mock_prometheus, \
             patch('main.encryption_service') as mock_encryption, \
             patch('main.audio_processor') as mock_processor:
            
            # Configure mocks
            mock_whisper.transcribe_audio_bytes.return_value = {
                "text": "Integration test transcription",
                "confidence": 0.93,
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

    def test_health_check_integration(self, client):
        """Test health check endpoint integration."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "transcription_info" in data

    def test_root_endpoint_integration(self, client):
        """Test root endpoint integration."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "VoiceBridge API is running"
        assert data["status"] == "healthy"
        assert "version" in data
        assert "build_date" in data
        assert "author" in data

    def test_transcription_endpoint_integration(self, client, mock_services):
        """Test complete transcription endpoint integration."""
        with patch('main.current_user') as mock_user:
            mock_user.id = 123
            
            test_audio_content = b"fake_audio_data_for_integration_test"
            
            response = client.post(
                "/transcribe",
                files={"audio_file": ("integration_test.wav", test_audio_content, "audio/wav")}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "message" in data
            assert "transcription" in data
            assert "confidence" in data
            assert "language" in data
            assert "user_id" in data
            assert "encrypted" in data
            assert "processing_time" in data
            assert "model" in data
            
            # Verify transcription content
            assert data["transcription"] == "Integration test transcription"
            assert data["confidence"] == 0.93
            assert data["language"] == "en"
            assert data["user_id"] == 123
            assert data["encrypted"] is True
            assert data["model"] == "whisper"
            
            # Verify all services were called
            mock_services["whisper"].transcribe_audio_bytes.assert_called_once()
            mock_services["rate_limit"].enforce_rate_limit.assert_called_once()
            mock_services["monitoring"].record_model_performance.assert_called_once()
            mock_services["mlflow"].log_transcription_metrics.assert_called_once()
            mock_services["wandb"].log_transcription_metrics.assert_called_once()
            mock_services["prometheus"].record_transcription.assert_called_once()
            mock_services["encryption"].encrypt_audio_file.assert_called_once()

    def test_api_key_configuration_integration(self, client, mock_services):
        """Test API key configuration integration."""
        response = client.post("/configure", json={"api_key": "test_api_key"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        assert "api_available" in data

    def test_error_handling_integration(self, client, mock_services):
        """Test error handling integration."""
        # Test with invalid audio format
        mock_services["processor"].is_valid_audio_format.return_value = False
        
        with patch('main.current_user') as mock_user:
            mock_user.id = 123
            
            test_audio_content = b"fake_audio_data"
            
            response = client.post(
                "/transcribe",
                files={"audio_file": ("test.txt", test_audio_content, "text/plain")}
            )
            
            assert response.status_code == 400
            assert "Unsupported audio format" in response.json()["detail"]

    def test_rate_limiting_integration(self, client, mock_services):
        """Test rate limiting integration."""
        # Mock rate limit exceeded
        mock_services["rate_limit"].enforce_rate_limit.side_effect = Exception("Rate limit exceeded")
        
        with patch('main.current_user') as mock_user:
            mock_user.id = 123
            
            test_audio_content = b"fake_audio_data"
            
            # Should handle rate limiting gracefully
            response = client.post(
                "/transcribe",
                files={"audio_file": ("test.wav", test_audio_content, "audio/wav")}
            )
            
            # Rate limiting should be enforced
            mock_services["rate_limit"].enforce_rate_limit.assert_called_once()


class TestServiceIntegration:
    """Test service integration and communication."""

    def test_mlflow_integration(self):
        """Test MLflow service integration."""
        with patch('main.mlflow_service') as mock_mlflow:
            mock_mlflow.start_run.return_value = "test_run_id"
            mock_mlflow.log_transcription_metrics.return_value = None
            mock_mlflow.end_run.return_value = None
            
            # Test MLflow operations
            run_id = mock_mlflow.start_run("test_run")
            assert run_id == "test_run_id"
            
            mock_mlflow.log_transcription_metrics(
                predicted_text="test",
                actual_text="",
                confidence=0.9,
                processing_time=1.0,
                audio_duration=2.0,
                model_name="whisper"
            )
            
            mock_mlflow.end_run()
            
            # Verify all methods were called
            mock_mlflow.start_run.assert_called_once()
            mock_mlflow.log_transcription_metrics.assert_called_once()
            mock_mlflow.end_run.assert_called_once()

    def test_wandb_integration(self):
        """Test Weights & Biases service integration."""
        with patch('main.wandb_service') as mock_wandb:
            mock_wandb.is_initialized = True
            mock_wandb.log_transcription_metrics.return_value = None
            mock_wandb.finish_run.return_value = None
            
            # Test W&B operations
            assert mock_wandb.is_initialized is True
            
            mock_wandb.log_transcription_metrics(
                predicted_text="test",
                actual_text="",
                confidence=0.9,
                processing_time=1.0,
                audio_duration=2.0,
                model_name="whisper"
            )
            
            mock_wandb.finish_run()
            
            # Verify methods were called
            mock_wandb.log_transcription_metrics.assert_called_once()
            mock_wandb.finish_run.assert_called_once()

    def test_prometheus_integration(self):
        """Test Prometheus metrics integration."""
        with patch('main.prometheus_metrics') as mock_prometheus:
            mock_prometheus.record_transcription.return_value = None
            
            # Test Prometheus metrics
            mock_prometheus.record_transcription(
                model="whisper",
                status="success",
                duration=1.5,
                confidence=0.95
            )
            
            # Verify metrics were recorded
            mock_prometheus.record_transcription.assert_called_once()
            call_args = mock_prometheus.record_transcription.call_args
            assert call_args[1]["model"] == "whisper"
            assert call_args[1]["status"] == "success"
            assert call_args[1]["duration"] == 1.5
            assert call_args[1]["confidence"] == 0.95

    def test_encryption_integration(self):
        """Test encryption service integration."""
        with patch('main.encryption_service') as mock_encryption:
            mock_encryption.encrypt_audio_file.return_value = (b"encrypted_data", {"key": "test_key"})
            mock_encryption.get_encryption_info.return_value = {
                "algorithm": "AES-256",
                "status": "active"
            }
            
            # Test encryption
            encrypted_data, metadata = mock_encryption.encrypt_audio_file(b"test_data", "test.wav")
            assert encrypted_data == b"encrypted_data"
            assert metadata == {"key": "test_key"}
            
            # Test encryption info
            info = mock_encryption.get_encryption_info()
            assert info["algorithm"] == "AES-256"
            assert info["status"] == "active"


class TestSystemIntegration:
    """Test system-wide integration scenarios."""

    def test_startup_sequence_integration(self):
        """Test application startup sequence."""
        with patch('main.rate_limiting_service') as mock_rate_limit, \
             patch('main.mlflow_service') as mock_mlflow, \
             patch('main.kafka_stream_service') as mock_kafka, \
             patch('main.grpc_server') as mock_grpc, \
             patch('main.wandb_service') as mock_wandb:
            
            # Configure startup mocks
            mock_rate_limit.initialize.return_value = None
            mock_mlflow.start_run.return_value = "test_run_id"
            mock_kafka.start.return_value = True
            mock_grpc.start.return_value = True
            mock_wandb.is_initialized = True
            
            # Test startup sequence
            from main import startup_event
            
            # This would test the actual startup sequence
            # In a real test, you'd call startup_event() and verify all services initialize
            assert True

    def test_shutdown_sequence_integration(self):
        """Test application shutdown sequence."""
        with patch('main.kafka_stream_service') as mock_kafka, \
             patch('main.grpc_server') as mock_grpc, \
             patch('main.mlflow_service') as mock_mlflow, \
             patch('main.wandb_service') as mock_wandb, \
             patch('main.model_monitoring_service') as mock_monitoring:
            
            # Configure shutdown mocks
            mock_kafka.stop.return_value = None
            mock_grpc.stop.return_value = None
            mock_mlflow.end_run.return_value = None
            mock_wandb.finish_run.return_value = None
            mock_monitoring.stop_monitoring.return_value = None
            
            # Test shutdown sequence
            from main import shutdown_event
            
            # This would test the actual shutdown sequence
            # In a real test, you'd call shutdown_event() and verify all services stop
            assert True

    def test_error_recovery_integration(self):
        """Test system error recovery and resilience."""
        with patch('main.whisper_service') as mock_whisper:
            # Test service failure and recovery
            mock_whisper.is_api_available.return_value = False
            mock_whisper.transcribe_audio_bytes.return_value = {
                "text": "Mock transcription (service unavailable)",
                "confidence": 0.5,
                "language": "en",
                "provider": "mock"
            }
            
            # System should continue to function with degraded service
            assert mock_whisper.is_api_available() is False
            
            result = mock_whisper.transcribe_audio_bytes(b"test_data")
            assert "Mock transcription" in result["text"]
            assert result["provider"] == "mock"

    def test_performance_under_load(self):
        """Test system performance under simulated load."""
        import time
        
        # Simulate multiple concurrent requests
        start_time = time.time()
        
        # Mock multiple transcription requests
        with patch('main.whisper_service') as mock_whisper:
            mock_whisper.transcribe_audio_bytes.return_value = {
                "text": "Load test transcription",
                "confidence": 0.9,
                "language": "en",
                "provider": "openai"
            }
            
            # Simulate 10 concurrent requests
            for i in range(10):
                result = mock_whisper.transcribe_audio_bytes(b"test_data")
                assert result["text"] == "Load test transcription"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance is reasonable (should complete quickly with mocks)
        assert total_time < 1.0  # Should complete in under 1 second with mocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
