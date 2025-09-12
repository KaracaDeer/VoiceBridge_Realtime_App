"""
Prometheus metrics service for VoiceBridge API
Handles system metrics collection and monitoring
"""
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict

import psutil
from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest
from prometheus_client.core import CollectorRegistry

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Prometheus metrics collector for VoiceBridge API"""

    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_metrics()
        self._start_system_metrics_collector()

    def _setup_metrics(self):
        """Setup Prometheus metrics"""

        # API Request Metrics
        self.request_count = Counter(
            "voicebridge_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "voicebridge_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Authentication Metrics
        self.auth_attempts = Counter(
            "voicebridge_auth_attempts_total",
            "Total authentication attempts",
            ["status"],  # success, failure
            registry=self.registry,
        )

        self.active_sessions = Gauge(
            "voicebridge_active_sessions",
            "Number of active user sessions",
            registry=self.registry,
        )

        # Transcription Metrics
        self.transcription_requests = Counter(
            "voicebridge_transcription_requests_total",
            "Total transcription requests",
            ["model", "status"],  # whisper, wav2vec, success, failure
            registry=self.registry,
        )

        self.transcription_duration = Histogram(
            "voicebridge_transcription_duration_seconds",
            "Transcription processing duration",
            ["model"],
            registry=self.registry,
        )

        self.transcription_confidence = Histogram(
            "voicebridge_transcription_confidence",
            "Transcription confidence scores",
            ["model"],
            registry=self.registry,
        )

        # WebSocket Metrics
        self.websocket_connections = Gauge(
            "voicebridge_websocket_connections",
            "Number of active WebSocket connections",
            registry=self.registry,
        )

        self.websocket_messages = Counter(
            "voicebridge_websocket_messages_total",
            "Total WebSocket messages processed",
            ["type"],  # audio, transcription, error
            registry=self.registry,
        )

        # Rate Limiting Metrics
        self.rate_limit_hits = Counter(
            "voicebridge_rate_limit_hits_total",
            "Total rate limit hits",
            ["endpoint", "client_type"],  # ip, user
            registry=self.registry,
        )

        # System Metrics
        self.cpu_usage = Gauge(
            "voicebridge_system_cpu_usage_percent",
            "System CPU usage percentage",
            registry=self.registry,
        )

        self.memory_usage = Gauge(
            "voicebridge_system_memory_usage_percent",
            "System memory usage percentage",
            registry=self.registry,
        )

        self.disk_usage = Gauge(
            "voicebridge_system_disk_usage_percent",
            "System disk usage percentage",
            registry=self.registry,
        )

        self.audio_files_processed = Counter(
            "voicebridge_audio_files_processed_total",
            "Total audio files processed",
            ["format", "status"],  # wav, mp3, success, failure
            registry=self.registry,
        )

        self.audio_file_size = Histogram(
            "voicebridge_audio_file_size_bytes",
            "Audio file sizes in bytes",
            ["format"],
            registry=self.registry,
        )

        # Error Metrics
        self.errors_total = Counter(
            "voicebridge_errors_total",
            "Total number of errors",
            ["error_type", "component"],  # authentication, transcription, system
            registry=self.registry,
        )

        # Model Performance Metrics
        self.model_accuracy = Gauge(
            "voicebridge_model_accuracy",
            "Model accuracy score",
            ["model_name"],
            registry=self.registry,
        )

        self.model_latency = Histogram(
            "voicebridge_model_latency_seconds",
            "Model inference latency",
            ["model_name"],
            registry=self.registry,
        )

        # Application Info
        self.app_info = Info("voicebridge_app_info", "Application information", registry=self.registry)

        # Set application info
        self.app_info.info(
            {
                "version": "1.0.0",
                "name": "VoiceBridge API",
                "description": "Real-time speech-to-text API",
            }
        )

    def _start_system_metrics_collector(self):
        """Start background thread to collect system metrics"""

        def collect_system_metrics():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_usage.set(cpu_percent)

                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage.set(memory.percent)

                    # Disk usage
                    disk = psutil.disk_usage("/")
                    disk_percent = (disk.used / disk.total) * 100
                    self.disk_usage.set(disk_percent)

                    time.sleep(30)  # Collect every 30 seconds

                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                    time.sleep(60)  # Wait longer on error

        # Start background thread
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()
        logger.info("Started system metrics collector")

    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        self.request_count.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()

        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_auth_attempt(self, status: str):
        """Record authentication attempt"""
        self.auth_attempts.labels(status=status).inc()

    def record_transcription(self, model: str, status: str, duration: float, confidence: float = None):
        """Record transcription metrics"""
        self.transcription_requests.labels(model=model, status=status).inc()
        self.transcription_duration.labels(model=model).observe(duration)

        if confidence is not None:
            self.transcription_confidence.labels(model=model).observe(confidence)

    def record_websocket_connection(self, connected: bool):
        """Record WebSocket connection"""
        if connected:
            self.websocket_connections.inc()
        else:
            self.websocket_connections.dec()

    def record_websocket_message(self, message_type: str):
        """Record WebSocket message"""
        self.websocket_messages.labels(type=message_type).inc()

    def record_rate_limit_hit(self, endpoint: str, client_type: str):
        """Record rate limit hit"""
        self.rate_limit_hits.labels(endpoint=endpoint, client_type=client_type).inc()

    def record_audio_file(self, file_format: str, status: str, file_size: int):
        """Record audio file processing"""
        self.audio_files_processed.labels(format=file_format, status=status).inc()
        self.audio_file_size.labels(format=file_format).observe(file_size)

    def record_error(self, error_type: str, component: str):
        """Record error occurrence"""
        self.errors_total.labels(error_type=error_type, component=component).inc()

    def record_model_performance(self, model_name: str, accuracy: float, latency: float):
        """Record model performance metrics"""
        self.model_accuracy.labels(model_name=model_name).set(accuracy)
        self.model_latency.labels(model_name=model_name).observe(latency)

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        return str(generate_latest(self.registry).decode("utf-8"))

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect and return metrics as dictionary"""
        return self.get_metrics_dict()

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary for API responses"""
        try:
            metrics_text = self.get_metrics()
            metrics_dict = {}

            for line in metrics_text.split("\n"):
                if line and not line.startswith("#"):
                    parts = line.split(" ")
                    if len(parts) >= 2:
                        metric_name = parts[0]
                        metric_value = parts[1]
                        metrics_dict[metric_name] = float(metric_value)

            return metrics_dict

        except Exception as e:
            logger.error(f"Error getting metrics dict: {e}")
            return {}

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3),
                "active_websocket_connections": self.websocket_connections._value._value,
                "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
            }

        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e),
            }


# Global Prometheus metrics instance
prometheus_metrics = PrometheusMetrics()
