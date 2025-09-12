"""
MLFlow service for VoiceBridge API
Handles model tracking, experiment management, and performance metrics
"""
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import mlflow
import mlflow.pytorch
import mlflow.sklearn
import numpy as np

logger = logging.getLogger(__name__)


class MLFlowService:
    """Service for MLFlow model tracking and experiment management"""

    def __init__(self):
        self.mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.experiment_name = "voicebridge-speech-recognition"
        self.current_run = None
        self.experiment_id = None

        # Initialize MLFlow
        self._setup_mlflow()

    def _setup_mlflow(self):
        """Setup MLFlow tracking"""
        try:
            # Check if MLFlow server is available
            import requests

            try:
                response = requests.get(f"{self.mlflow_uri}/health", timeout=10)
                if response.status_code == 200:
                    mlflow.set_tracking_uri(self.mlflow_uri)
                    logger.info(f"Connected to MLFlow server at {self.mlflow_uri}")
                else:
                    raise Exception("MLFlow server not responding")
            except Exception as e:
                logger.warning(f"MLFlow server not available: {e}")
                logger.info("MLFlow disabled - using mock mode")
                self.mlflow_uri = None
                self.experiment_id = None
                return

            # Create or get experiment
            try:
                experiment = mlflow.get_experiment_by_name(self.experiment_name)
                if experiment is None:
                    self.experiment_id = mlflow.create_experiment(self.experiment_name)
                    logger.info(f"Created new MLFlow experiment: {self.experiment_name}")
                else:
                    self.experiment_id = experiment.experiment_id
                    logger.info(f"Using existing MLFlow experiment: {self.experiment_name}")
            except Exception as e:
                logger.warning(f"Failed to setup MLFlow experiment: {e}")
                # Fallback to default experiment
                self.experiment_id = "0"

        except Exception as e:
            logger.error(f"Failed to initialize MLFlow: {e}")
            self.mlflow_uri = None

    def start_run(self, run_name: str = None, tags: Dict[str, str] = None) -> str:
        """
        Start a new MLFlow run

        Args:
            run_name: Name for the run
            tags: Tags to associate with the run

        Returns:
            Run ID
        """
        if not self.mlflow_uri:
            logger.warning("MLFlow not available, skipping run start")
            return None

        try:
            with mlflow.start_run(experiment_id=self.experiment_id, run_name=run_name) as run:
                self.current_run = run

                # Add tags
                if tags:
                    mlflow.set_tags(tags)

                # Add system info
                mlflow.set_tag("system", "voicebridge")
                mlflow.set_tag("timestamp", datetime.utcnow().isoformat())

                logger.info(f"Started MLFlow run: {run.info.run_id}")
                return str(run.info.run_id)

        except Exception as e:
            logger.error(f"Failed to start MLFlow run: {e}")
            return None

    def log_model_parameters(self, params: Dict[str, Any]):
        """Log model parameters"""
        if not self.current_run:
            return

        try:
            mlflow.log_params(params)
            logger.debug(f"Logged model parameters: {list(params.keys())}")
        except Exception as e:
            logger.error(f"Failed to log parameters: {e}")

    def log_model_metrics(self, metrics: Dict[str, float]):
        """Log model metrics"""
        if not self.current_run:
            return

        try:
            mlflow.log_metrics(metrics)
            logger.debug(f"Logged model metrics: {list(metrics.keys())}")
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    def log_transcription_metrics(
        self,
        predicted_text: str,
        actual_text: str,
        confidence: float,
        processing_time: float,
        audio_duration: float,
        model_name: str = "whisper",
    ):
        """
        Log transcription-specific metrics

        Args:
            predicted_text: Predicted transcription text
            actual_text: Actual/ground truth text
            confidence: Model confidence score
            processing_time: Time taken for processing
            audio_duration: Duration of audio file
            model_name: Name of the model used
        """
        if not self.current_run:
            return

        try:
            # Calculate text similarity metrics
            similarity_metrics = self._calculate_text_similarity(predicted_text, actual_text)

            # Log metrics
            metrics = {
                "confidence": confidence,
                "processing_time": processing_time,
                "audio_duration": audio_duration,
                "processing_speed_ratio": processing_time / audio_duration if audio_duration > 0 else 0,
                **similarity_metrics,
            }

            mlflow.log_metrics(metrics)

            # Log model info
            mlflow.set_tag("model_name", model_name)
            mlflow.set_tag("has_ground_truth", bool(actual_text))

            logger.debug(f"Logged transcription metrics for {model_name}")

        except Exception as e:
            logger.error(f"Failed to log transcription metrics: {e}")

    def _calculate_text_similarity(self, predicted: str, actual: str) -> Dict[str, float]:
        """Calculate text similarity metrics"""
        if not actual:
            return {
                "text_length": len(predicted),
                "word_count": len(predicted.split()),
                "has_prediction": bool(predicted),
            }

        # Simple character-level similarity
        predicted_lower = predicted.lower().strip()
        actual_lower = actual.lower().strip()

        # Character-level accuracy
        char_accuracy = self._calculate_character_accuracy(predicted_lower, actual_lower)

        # Word-level accuracy
        predicted_words = predicted_lower.split()
        actual_words = actual_lower.split()
        word_accuracy = self._calculate_word_accuracy(predicted_words, actual_words)

        # Length metrics
        length_ratio = len(predicted_lower) / len(actual_lower) if len(actual_lower) > 0 else 0

        return {
            "char_accuracy": char_accuracy,
            "word_accuracy": word_accuracy,
            "length_ratio": length_ratio,
            "predicted_length": len(predicted_lower),
            "actual_length": len(actual_lower),
            "predicted_word_count": len(predicted_words),
            "actual_word_count": len(actual_words),
        }

    def _calculate_character_accuracy(self, predicted: str, actual: str) -> float:
        """Calculate character-level accuracy"""
        if not actual:
            return 0.0

        # Simple edit distance-based accuracy
        max_len = max(len(predicted), len(actual))
        if max_len == 0:
            return 1.0

        # Calculate Levenshtein distance
        distance = self._levenshtein_distance(predicted, actual)
        return 1.0 - (distance / max_len)

    def _calculate_word_accuracy(self, predicted_words: List[str], actual_words: List[str]) -> float:
        """Calculate word-level accuracy"""
        if not actual_words:
            return 0.0

        if not predicted_words:
            return 0.0

        # Simple word matching
        matches = 0
        for pred_word in predicted_words:
            if pred_word in actual_words:
                matches += 1

        return matches / len(actual_words)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def log_model_artifact(self, artifact_path: str, artifact_name: str = None):
        """Log model artifacts"""
        if not self.current_run:
            return

        try:
            mlflow.log_artifact(artifact_path, artifact_name)
            logger.debug(f"Logged artifact: {artifact_path}")
        except Exception as e:
            logger.error(f"Failed to log artifact: {e}")

    def log_model(self, model, model_name: str, model_type: str = "pytorch"):
        """Log trained model"""
        if not self.current_run:
            return

        try:
            if model_type == "pytorch":
                mlflow.pytorch.log_model(model, model_name)
            elif model_type == "sklearn":
                mlflow.sklearn.log_model(model, model_name)
            else:
                mlflow.log_model(model, model_name)

            logger.info(f"Logged model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to log model: {e}")

    def log_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        gpu_usage: float = None,
    ):
        """Log system performance metrics"""
        if not self.current_run:
            return

        try:
            metrics = {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage,
                "disk_usage_percent": disk_usage,
            }

            if gpu_usage is not None:
                metrics["gpu_usage_percent"] = gpu_usage

            mlflow.log_metrics(metrics)
            logger.debug("Logged system metrics")

        except Exception as e:
            logger.error(f"Failed to log system metrics: {e}")

    def end_run(self, status: str = "FINISHED"):
        """End current MLFlow run"""
        if not self.current_run:
            return

        try:
            mlflow.end_run(status=status)
            logger.info(f"Ended MLFlow run: {self.current_run.info.run_id}")
            self.current_run = None
        except Exception as e:
            logger.error(f"Failed to end MLFlow run: {e}")

    def get_experiment_runs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent experiment runs"""
        if not self.mlflow_uri:
            return []

        try:
            runs = mlflow.search_runs(
                experiment_ids=[self.experiment_id],
                max_results=limit,
                order_by=["start_time DESC"],
            )

            return list(runs.to_dict("records"))
        except Exception as e:
            logger.error(f"Failed to get experiment runs: {e}")
            return []

    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Get model performance summary"""
        try:
            runs = self.get_experiment_runs(limit=50)

            if not runs:
                return {"error": "No runs found"}

            # Calculate summary statistics
            confidences = [run.get("metrics.confidence", 0) for run in runs if "metrics.confidence" in run]
            processing_times = [
                run.get("metrics.processing_time", 0) for run in runs if "metrics.processing_time" in run
            ]
            char_accuracies = [run.get("metrics.char_accuracy", 0) for run in runs if "metrics.char_accuracy" in run]

            summary = {
                "total_runs": len(runs),
                "average_confidence": np.mean(confidences) if confidences else 0,
                "average_processing_time": np.mean(processing_times) if processing_times else 0,
                "average_char_accuracy": np.mean(char_accuracies) if char_accuracies else 0,
                "latest_run": runs[0] if runs else None,
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {"error": str(e)}


# Global MLFlow service instance
mlflow_service = MLFlowService()
