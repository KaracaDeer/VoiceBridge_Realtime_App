"""
Model monitoring service for VoiceBridge API
Handles model performance tracking, drift detection, and error analysis
"""
# type: ignore
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np

from src.services.mlflow_service import mlflow_service
from src.services.prometheus_service import prometheus_metrics
from src.services.wandb_service import wandb_service

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics data class"""

    model_name: str
    timestamp: datetime
    accuracy: float
    confidence: float
    processing_time: float
    error_rate: float
    throughput: float
    latency_p95: float
    latency_p99: float


@dataclass
class ModelDriftAlert:
    """Model drift alert data class"""

    model_name: str
    metric_name: str
    current_value: float
    baseline_value: float
    drift_percentage: float
    severity: str  # low, medium, high, critical
    timestamp: datetime


class ModelMonitoringService:
    """Service for monitoring model performance and detecting issues"""

    def __init__(self):
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))
        self.baseline_metrics = {}
        self.drift_thresholds = {
            "accuracy": 0.05,  # 5% decrease
            "confidence": 0.10,  # 10% decrease
            "processing_time": 0.20,  # 20% increase
            "error_rate": 0.15,  # 15% increase
        }
        self.alert_history: deque = deque(maxlen=100)
        self.monitoring_active = True

        # Start background monitoring
        self._start_background_monitoring()

    def _start_background_monitoring(self):
        """Start background monitoring thread"""

        def monitor_models():
            while self.monitoring_active:
                try:
                    self._check_model_drift()
                    self._update_baseline_metrics()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Error in background monitoring: {e}")
                    time.sleep(300)  # Wait 5 minutes on error

        thread = threading.Thread(target=monitor_models, daemon=True)
        thread.start()
        logger.info("Started model monitoring background thread")

    def record_model_performance(
        self,
        model_name: str,
        accuracy: float,
        confidence: float,
        processing_time: float,
        error_occurred: bool = False,
    ):
        """
        Record model performance metrics

        Args:
            model_name: Name of the model
            accuracy: Model accuracy score
            confidence: Model confidence score
            processing_time: Processing time in seconds
            error_occurred: Whether an error occurred
        """
        try:
            timestamp = datetime.utcnow()

            # Calculate error rate
            error_rate = 1.0 if error_occurred else 0.0

            # Create performance metrics
            metrics = ModelPerformanceMetrics(
                model_name=model_name,
                timestamp=timestamp,
                accuracy=accuracy,
                confidence=confidence,
                processing_time=processing_time,
                error_rate=error_rate,
                throughput=1.0 / processing_time if processing_time > 0 else 0,
                latency_p95=processing_time,
                latency_p99=processing_time,
            )

            # Store in history
            self.performance_history[model_name].append(metrics)

            # Log to MLFlow
            mlflow_service.log_model_metrics(
                {
                    f"{model_name}_accuracy": accuracy,
                    f"{model_name}_confidence": confidence,
                    f"{model_name}_processing_time": processing_time,
                    f"{model_name}_error_rate": error_rate,
                }
            )

            # Log to W&B
            wandb_service.log_transcription_metrics(
                predicted_text="",  # Not available in this context
                actual_text="",
                confidence=confidence,
                processing_time=processing_time,
                audio_duration=0,
                model_name=model_name,
            )

            # Update Prometheus metrics
            prometheus_metrics.record_model_performance(model_name, accuracy, processing_time)

            logger.debug(f"Recorded performance metrics for {model_name}")

        except Exception as e:
            logger.error(f"Failed to record model performance: {e}")

    def _check_model_drift(self):
        """Check for model drift and generate alerts"""
        try:
            for model_name, history in self.performance_history.items():
                if len(history) < 10:  # Need minimum data points
                    continue

                # Get recent metrics (last 100 points)
                recent_metrics = list(history)[-100:]

                # Calculate current averages
                current_metrics = self._calculate_metrics_average(recent_metrics)

                # Get baseline metrics
                baseline = self.baseline_metrics.get(model_name, {})

                if not baseline:
                    # Set initial baseline
                    self.baseline_metrics[model_name] = current_metrics
                    continue

                # Check for drift
                for metric_name, threshold in self.drift_thresholds.items():
                    current_value = current_metrics.get(metric_name, 0)
                    baseline_value = baseline.get(metric_name, 0)

                    if baseline_value == 0:
                        continue

                    # Calculate drift percentage
                    if metric_name in ["processing_time", "error_rate"]:
                        # For these metrics, increase is bad
                        drift_percentage = (current_value - baseline_value) / baseline_value
                    else:
                        # For accuracy and confidence, decrease is bad
                        drift_percentage = (baseline_value - current_value) / baseline_value

                    # Check if drift exceeds threshold
                    if drift_percentage > threshold:
                        severity = self._determine_severity(drift_percentage, threshold)

                        alert = ModelDriftAlert(
                            model_name=model_name,
                            metric_name=metric_name,
                            current_value=current_value,
                            baseline_value=baseline_value,
                            drift_percentage=drift_percentage,
                            severity=severity,
                            timestamp=datetime.utcnow(),
                        )

                        self.alert_history.append(alert)
                        self._handle_drift_alert(alert)

        except Exception as e:
            logger.error(f"Error checking model drift: {e}")

    def _calculate_metrics_average(self, metrics_list: List[ModelPerformanceMetrics]) -> Dict[str, float]:
        """Calculate average metrics from a list of performance metrics"""
        if not metrics_list:
            return {}

        return {
            "accuracy": float(np.mean([m.accuracy for m in metrics_list])),
            "confidence": float(np.mean([m.confidence for m in metrics_list])),
            "processing_time": float(np.mean([m.processing_time for m in metrics_list])),
            "error_rate": float(np.mean([m.error_rate for m in metrics_list])),
            "throughput": float(np.mean([m.throughput for m in metrics_list])),
            "latency_p95": float(np.percentile([m.latency_p95 for m in metrics_list], 95)),
            "latency_p99": float(np.percentile([m.latency_p99 for m in metrics_list], 99)),
        }

    def _determine_severity(self, drift_percentage: float, threshold: float) -> str:
        """Determine alert severity based on drift percentage"""
        if drift_percentage > threshold * 3:
            return "critical"
        elif drift_percentage > threshold * 2:
            return "high"
        elif drift_percentage > threshold * 1.5:
            return "medium"
        else:
            return "low"

    def _handle_drift_alert(self, alert: ModelDriftAlert):
        """Handle model drift alert"""
        try:
            # Log alert
            logger.warning(
                f"Model drift detected: {alert.model_name} - {alert.metric_name} "
                f"drifted {alert.drift_percentage:.2%} (severity: {alert.severity})"
            )

            # Log to Prometheus
            prometheus_metrics.record_error(error_type="model_drift", component=alert.model_name)

            # Log to MLFlow
            mlflow_service.log_model_metrics(
                {
                    f"{alert.model_name}_drift_{alert.metric_name}": alert.drift_percentage,
                    f"{alert.model_name}_alert_severity": 1 if alert.severity == "critical" else 0,
                }
            )

            # Send notification (implement based on your notification system)
            self._send_drift_notification(alert)

        except Exception as e:
            logger.error(f"Failed to handle drift alert: {e}")

    def _send_drift_notification(self, alert: ModelDriftAlert):
        """Send drift notification (implement based on your notification system)"""
        # This could be implemented to send emails, Slack messages, etc.
        logger.info(
            f"DRIFT ALERT: {alert.model_name} - {alert.metric_name} "
            f"({alert.severity.upper()}) - {alert.drift_percentage:.2%} drift"
        )

    def _update_baseline_metrics(self):
        """Update baseline metrics periodically"""
        try:
            for model_name, history in self.performance_history.items():
                if len(history) < 50:  # Need sufficient data
                    continue

                # Use last 200 points for baseline calculation
                baseline_data = list(history)[-200:]
                baseline_metrics = self._calculate_metrics_average(baseline_data)

                self.baseline_metrics[model_name] = baseline_metrics

        except Exception as e:
            logger.error(f"Failed to update baseline metrics: {e}")

    def get_performance_metrics(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific model"""
        try:
            if model_name not in self.performance_history:
                return {"error": f"Model {model_name} not found"}

            history = list(self.performance_history[model_name])
            if not history:
                return {"error": f"No performance data for model {model_name}"}

            # Calculate summary statistics
            recent_metrics = history[-100:] if len(history) >= 100 else history

            return {
                "model_name": model_name,
                "total_predictions": len(history),
                "recent_predictions": len(recent_metrics),
                "average_accuracy": float(np.mean([m.accuracy for m in recent_metrics])),
                "average_confidence": float(np.mean([m.confidence for m in recent_metrics])),
                "average_processing_time": float(np.mean([m.processing_time for m in recent_metrics])),
                "average_error_rate": float(np.mean([m.error_rate for m in recent_metrics])),
                "p95_latency": float(np.percentile([m.processing_time for m in recent_metrics], 95)),
                "p99_latency": float(np.percentile([m.processing_time for m in recent_metrics], 99)),
                "baseline_metrics": self.baseline_metrics.get(model_name, {}),
                "last_updated": history[-1].timestamp.isoformat() if history else None,
            }

        except Exception as e:
            logger.error(f"Failed to get performance metrics for {model_name}: {e}")
            return {"error": str(e)}

    def get_model_performance_summary(self, model_name: str = None) -> Dict[str, Any]:
        """Get model performance summary"""
        try:
            if model_name:
                models = [model_name] if model_name in self.performance_history else []
            else:
                models = list(self.performance_history.keys())

            summary = {}

            for model in models:
                history = list(self.performance_history[model])
                if not history:
                    continue

                # Calculate summary statistics
                recent_metrics = history[-100:] if len(history) >= 100 else history

                summary[model] = {
                    "total_predictions": len(history),
                    "recent_predictions": len(recent_metrics),
                    "average_accuracy": np.mean([m.accuracy for m in recent_metrics]),
                    "average_confidence": np.mean([m.confidence for m in recent_metrics]),
                    "average_processing_time": np.mean([m.processing_time for m in recent_metrics]),
                    "average_error_rate": np.mean([m.error_rate for m in recent_metrics]),
                    "p95_latency": np.percentile([m.processing_time for m in recent_metrics], 95),
                    "p99_latency": np.percentile([m.processing_time for m in recent_metrics], 99),
                    "baseline_metrics": self.baseline_metrics.get(model, {}),
                    "last_updated": history[-1].timestamp.isoformat() if history else None,
                }

            return summary

        except Exception as e:
            logger.error(f"Failed to get model performance summary: {e}")
            return {"error": str(e)}

    def get_drift_alerts(self, model_name: str = None, severity: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get drift alerts"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            alerts = []
            for alert in self.alert_history:
                if alert.timestamp < cutoff_time:
                    continue

                if model_name and alert.model_name != model_name:
                    continue

                if severity and alert.severity != severity:
                    continue

                alerts.append(
                    {
                        "model_name": alert.model_name,
                        "metric_name": alert.metric_name,
                        "current_value": alert.current_value,
                        "baseline_value": alert.baseline_value,
                        "drift_percentage": alert.drift_percentage,
                        "severity": alert.severity,
                        "timestamp": alert.timestamp.isoformat(),
                    }
                )

            # Sort by timestamp (newest first)
            alerts.sort(key=lambda x: x["timestamp"], reverse=True)

            return alerts

        except Exception as e:
            logger.error(f"Failed to get drift alerts: {e}")
            return []

    def get_model_health_status(self) -> Dict[str, Any]:
        """Get overall model health status"""
        try:
            health_status = {
                "overall_status": "healthy",
                "models": {},
                "total_alerts": len(self.alert_history),
                "critical_alerts": len([a for a in self.alert_history if a.severity == "critical"]),
                "timestamp": datetime.utcnow().isoformat(),
            }

            for model_name in self.performance_history.keys():
                recent_alerts = [
                    a
                    for a in self.alert_history
                    if a.model_name == model_name and a.timestamp > datetime.utcnow() - timedelta(hours=1)
                ]

                if any(a.severity == "critical" for a in recent_alerts):
                    status = "critical"
                elif any(a.severity == "high" for a in recent_alerts):
                    status = "warning"
                elif any(a.severity in ["medium", "low"] for a in recent_alerts):
                    status = "degraded"
                else:
                    status = "healthy"

                model_info = {
                    "status": status,
                    "recent_alerts": len(recent_alerts),
                    "baseline_available": model_name in self.baseline_metrics,
                }
                models_dict = health_status["models"]
                models_dict[model_name] = model_info

            # Determine overall status
            models_values = health_status["models"].values()
            model_statuses = [model["status"] for model in models_values]
            if "critical" in model_statuses:
                health_status["overall_status"] = "critical"
            elif "warning" in model_statuses:
                health_status["overall_status"] = "warning"
            elif "degraded" in model_statuses:
                health_status["overall_status"] = "degraded"

            return health_status

        except Exception as e:
            logger.error(f"Failed to get model health status: {e}")
            return {"error": str(e), "overall_status": "error"}

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        logger.info("Model monitoring stopped")


# Global model monitoring service instance
model_monitoring_service = ModelMonitoringService()
