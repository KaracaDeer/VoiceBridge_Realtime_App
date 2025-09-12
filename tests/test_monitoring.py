"""
Monitoring and logging systems test suite.
"""
import pytest  # noqa: F401

from src.services.mlflow_service import mlflow_service
from src.services.model_monitoring_service import model_monitoring_service
from src.services.prometheus_service import prometheus_metrics
from src.services.wandb_service import wandb_service


class TestMonitoring:
    """Test monitoring and logging functionality."""

    def test_mlflow_service(self):
        """Test MLFlow service functionality."""
        # Test MLFlow initialization
        assert mlflow_service is not None

        # MLflow URI can be None if server is not available (mock mode)
        # This is expected behavior when MLflow server is not running
        if mlflow_service.mlflow_uri is not None:
            # Test run creation only if MLflow is available
            run_id = mlflow_service.start_run("test-run", {"test": "tag"})
            assert run_id is not None

            # Test metrics logging
            mlflow_service.log_transcription_metrics(
                predicted_text="test transcription",
                actual_text="test ground truth",
                confidence=0.95,
                processing_time=1.5,
                audio_duration=2.0,
                model_name="whisper",
            )

            # End run
            mlflow_service.end_run()
        else:
            # Test mock mode functionality
            run_id = mlflow_service.start_run("test-run", {"test": "tag"})
            assert run_id is None  # Should return None in mock mode

            # Test metrics logging (should not fail in mock mode)
            mlflow_service.log_transcription_metrics(
                predicted_text="test transcription",
                actual_text="test ground truth",
                confidence=0.95,
                processing_time=1.5,
                audio_duration=2.0,
                model_name="whisper",
            )

            # End run (should not fail in mock mode)
            mlflow_service.end_run()

        return True

    def test_prometheus_metrics(self):
        """Test Prometheus metrics collection."""
        # Test metrics recording
        prometheus_metrics.record_transcription(model="whisper", status="success", duration=1.5, confidence=0.95)

        # Test metrics collection
        metrics = prometheus_metrics.collect_metrics()
        assert metrics is not None
        return True

    def test_wandb_service(self):
        """Test Weights & Biases service."""
        # Test W&B initialization
        assert wandb_service is not None

        # Test metrics logging
        wandb_service.log_transcription_metrics(
            predicted_text="test transcription",
            actual_text="test ground truth",
            confidence=0.95,
            processing_time=1.5,
            audio_duration=2.0,
            model_name="whisper",
        )

        # Test run finishing
        wandb_service.finish_run()
        return True

    def test_model_monitoring(self):
        """Test model monitoring service."""
        # Test performance recording
        model_monitoring_service.record_model_performance(
            model_name="whisper",
            accuracy=0.95,
            confidence=0.95,
            processing_time=1.5,
            error_occurred=False,
        )

        # Test metrics collection
        metrics = model_monitoring_service.get_performance_metrics("whisper")
        assert metrics is not None
        return True

    def test_logging_configuration(self):
        """Test logging configuration."""
        import logging

        # Test logger configuration
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        # Test log message
        logger.info("Test log message")

        assert logger.level == logging.INFO
        return True

    def test_health_checks(self):
        """Test health check endpoints."""
        from fastapi.testclient import TestClient

        from main import app

        client = TestClient(app)

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        health_data = response.json()
        assert "status" in health_data
        assert "services" in health_data
        assert health_data["status"] == "healthy"
        return True
