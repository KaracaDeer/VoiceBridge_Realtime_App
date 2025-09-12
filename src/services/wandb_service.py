"""
Weights & Biases service for VoiceBridge API
Handles experiment tracking, model versioning, and visualization
"""
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import plotly.express as px

import wandb

logger = logging.getLogger(__name__)


class WandBService:
    """Service for Weights & Biases experiment tracking"""

    def __init__(self):
        self.project_name = "voicebridge-speech-recognition"
        self.entity = os.getenv("WANDB_ENTITY", None)
        self.api_key = os.getenv("WANDB_API_KEY", None)
        self.run = None
        self.is_initialized = False

        # Initialize W&B
        self._setup_wandb()

    def _setup_wandb(self) -> None:
        """Setup Weights & Biases"""
        try:
            if not self.api_key:
                logger.warning("WANDB_API_KEY not found, W&B tracking disabled")
                logger.info("Using W&B in mock mode (local tracking)")
                self.is_initialized = False
                return

            # Login to W&B
            wandb.login(key=self.api_key)  # type: ignore

            # Initialize run
            self.run = wandb.init(  # type: ignore
                project=self.project_name,
                entity=self.entity,
                name=f"voicebridge-run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                tags=["voicebridge", "speech-recognition", "api"],
                config={
                    "model_type": "whisper",
                    "language": "english",
                    "api_version": "1.0.0",
                    "framework": "fastapi",
                },
            )

            self.is_initialized = True
            logger.info("Weights & Biases initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Weights & Biases: {e}")
            logger.info("Using W&B in mock mode (local tracking)")
            self.is_initialized = False

    def log_transcription_metrics(
        self,
        predicted_text: str,
        actual_text: str,
        confidence: float,
        processing_time: float,
        audio_duration: float,
        model_name: str = "whisper",
        audio_features: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log transcription metrics to W&B

        Args:
            predicted_text: Predicted transcription
            actual_text: Ground truth text
            confidence: Model confidence
            processing_time: Processing time in seconds
            audio_duration: Audio duration in seconds
            model_name: Name of the model
            audio_features: Additional audio features
        """
        if not self.is_initialized:
            logger.info("W&B not initialized, using mock mode for metrics logging")
            # Mock logging - just log to console
            logger.info(
                f"Mock W&B Log - Model: {model_name}, Confidence: {confidence:.2f}, Processing Time: {processing_time:.2f}s"
            )
            return

        try:
            # Calculate metrics
            metrics = self._calculate_transcription_metrics(
                predicted_text, actual_text, confidence, processing_time, audio_duration
            )

            # Log metrics
            wandb.log(  # type: ignore
                {
                    "transcription/confidence": confidence,
                    "transcription/processing_time": processing_time,
                    "transcription/audio_duration": audio_duration,
                    "transcription/processing_speed_ratio": processing_time / audio_duration
                    if audio_duration > 0
                    else 0,
                    "transcription/char_accuracy": metrics.get("char_accuracy", 0),
                    "transcription/word_accuracy": metrics.get("word_accuracy", 0),
                    "transcription/length_ratio": metrics.get("length_ratio", 0),
                    "transcription/predicted_length": metrics.get("predicted_length", 0),
                    "transcription/actual_length": metrics.get("actual_length", 0),
                    "model_name": model_name,
                }
            )

            # Log audio features if provided
            if audio_features:
                wandb.log(  # type: ignore
                    {
                        "audio/sample_rate": audio_features.get("sample_rate", 0),
                        "audio/channels": audio_features.get("channels", 0),
                        "audio/bit_rate": audio_features.get("bit_rate", 0),
                        "audio/snr": audio_features.get("snr", 0),
                    }
                )

            logger.debug(f"Logged transcription metrics to W&B for {model_name}")

        except Exception as e:
            logger.error(f"Failed to log transcription metrics to W&B: {e}")

    def _calculate_transcription_metrics(
        self,
        predicted: str,
        actual: str,
        confidence: float,
        processing_time: float,
        audio_duration: float,
    ) -> Dict[str, float]:
        """Calculate transcription metrics"""
        metrics = {
            "confidence": confidence,
            "processing_time": processing_time,
            "audio_duration": audio_duration,
            "processing_speed_ratio": processing_time / audio_duration if audio_duration > 0 else 0,
        }

        if not actual:
            metrics.update(
                {
                    "char_accuracy": 0,
                    "word_accuracy": 0,
                    "length_ratio": 0,
                    "predicted_length": len(predicted),
                    "actual_length": 0,
                }
            )
            return metrics

        # Calculate text similarity metrics
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

        metrics.update(
            {
                "char_accuracy": char_accuracy,
                "word_accuracy": word_accuracy,
                "length_ratio": length_ratio,
                "predicted_length": len(predicted_lower),
                "actual_length": len(actual_lower),
            }
        )

        return metrics

    def _calculate_character_accuracy(self, predicted: str, actual: str) -> float:
        """Calculate character-level accuracy using edit distance"""
        if not actual:
            return 0.0

        max_len = max(len(predicted), len(actual))
        if max_len == 0:
            return 1.0

        distance = self._levenshtein_distance(predicted, actual)
        return 1.0 - (distance / max_len)

    def _calculate_word_accuracy(self, predicted_words: List[str], actual_words: List[str]) -> float:
        """Calculate word-level accuracy"""
        if not actual_words:
            return 0.0

        if not predicted_words:
            return 0.0

        matches = sum(1 for word in predicted_words if word in actual_words)
        return matches / len(actual_words)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
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

    def log_model_performance(
        self,
        model_name: str,
        accuracy: float,
        precision: float,
        recall: float,
        f1_score: float,
        confusion_matrix: Optional[np.ndarray] = None,
    ) -> None:
        """Log model performance metrics"""
        if not self.is_initialized:
            return

        try:
            wandb.log(  # type: ignore
                {
                    f"model/{model_name}/accuracy": accuracy,
                    f"model/{model_name}/precision": precision,
                    f"model/{model_name}/recall": recall,
                    f"model/{model_name}/f1_score": f1_score,
                }
            )

            # Log confusion matrix if provided
            if confusion_matrix is not None:
                wandb.log(  # type: ignore
                    {
                        f"model/{model_name}/confusion_matrix": wandb.plot.confusion_matrix(  # type: ignore
                            probs=confusion_matrix, class_names=["Correct", "Incorrect"]
                        )
                    }
                )

            logger.debug(f"Logged model performance for {model_name}")

        except Exception as e:
            logger.error(f"Failed to log model performance: {e}")

    def log_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        gpu_usage: Optional[float] = None,
        network_io: Optional[Dict[str, float]] = None,
    ) -> None:
        """Log system performance metrics"""
        if not self.is_initialized:
            return

        try:
            metrics = {
                "system/cpu_usage": cpu_usage,
                "system/memory_usage": memory_usage,
                "system/disk_usage": disk_usage,
            }

            if gpu_usage is not None:
                metrics["system/gpu_usage"] = gpu_usage

            if network_io:
                metrics.update(
                    {
                        "system/network_bytes_sent": network_io.get("bytes_sent", 0),
                        "system/network_bytes_recv": network_io.get("bytes_recv", 0),
                    }
                )

            wandb.log(metrics)  # type: ignore
            logger.debug("Logged system metrics to W&B")

        except Exception as e:
            logger.error(f"Failed to log system metrics: {e}")

    def create_performance_plots(self, metrics_data: List[Dict[str, Any]], save_path: str = "plots") -> None:
        """Create and log performance visualization plots"""
        if not self.is_initialized:
            return

        try:
            os.makedirs(save_path, exist_ok=True)

            # Create confidence distribution plot
            confidences = [m.get("confidence", 0) for m in metrics_data]
            if confidences:
                fig = px.histogram(
                    x=confidences,
                    title="Transcription Confidence Distribution",
                    labels={"x": "Confidence Score", "y": "Count"},
                )
                fig.write_html(f"{save_path}/confidence_distribution.html")
                wandb.log(  # type: ignore
                    {
                        "plots/confidence_distribution": wandb.Html(  # type: ignore
                            open(f"{save_path}/confidence_distribution.html").read()
                        )
                    }
                )

            # Create processing time vs accuracy plot
            processing_times = [m.get("processing_time", 0) for m in metrics_data]
            accuracies = [m.get("char_accuracy", 0) for m in metrics_data]

            if processing_times and accuracies:
                fig = px.scatter(
                    x=processing_times,
                    y=accuracies,
                    title="Processing Time vs Accuracy",
                    labels={"x": "Processing Time (s)", "y": "Character Accuracy"},
                )
                fig.write_html(f"{save_path}/processing_vs_accuracy.html")
                wandb.log(  # type: ignore
                    {
                        "plots/processing_vs_accuracy": wandb.Html(  # type: ignore
                            open(f"{save_path}/processing_vs_accuracy.html").read()
                        )
                    }
                )

            # Create time series plot
            timestamps = [m.get("timestamp", i) for i, m in enumerate(metrics_data)]
            if timestamps and confidences:
                fig = px.line(
                    x=timestamps,
                    y=confidences,
                    title="Confidence Over Time",
                    labels={"x": "Time", "y": "Confidence Score"},
                )
                fig.write_html(f"{save_path}/confidence_timeline.html")
                wandb.log(  # type: ignore
                    {"plots/confidence_timeline": wandb.Html(open(f"{save_path}/confidence_timeline.html").read())}  # type: ignore
                )

            logger.info(f"Created performance plots in {save_path}")

        except Exception as e:
            logger.error(f"Failed to create performance plots: {e}")

    def log_audio_sample(
        self,
        audio_data: bytes,
        transcription: str,
        confidence: float,
        sample_name: Optional[str] = None,
    ) -> None:
        """Log audio sample with transcription"""
        if not self.is_initialized:
            return

        try:
            # Save audio file temporarily
            temp_path = f"temp_audio_{int(time.time())}.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_data)

            # Log to W&B
            wandb.log(  # type: ignore
                {
                    "audio_samples": wandb.Audio(  # type: ignore
                        temp_path,
                        caption=f"Transcription: {transcription} (Confidence: {confidence:.2f})",
                    )
                }
            )

            # Clean up
            os.remove(temp_path)

            logger.debug(f"Logged audio sample: {sample_name}")

        except Exception as e:
            logger.error(f"Failed to log audio sample: {e}")

    def log_model_artifact(self, model_path: str, model_name: str) -> None:
        """Log model artifact to W&B"""
        if not self.is_initialized:
            return

        try:
            artifact = wandb.Artifact(  # type: ignore
                name=model_name,
                type="model",
                description=f"VoiceBridge {model_name} model",
            )
            artifact.add_file(model_path)
            wandb.log_artifact(artifact)  # type: ignore

            logger.info(f"Logged model artifact: {model_name}")

        except Exception as e:
            logger.error(f"Failed to log model artifact: {e}")

    def finish_run(self) -> None:
        """Finish W&B run"""
        if self.is_initialized and self.run:
            try:
                wandb.finish()  # type: ignore
                logger.info("W&B run finished successfully")
            except Exception as e:
                logger.error(f"Failed to finish W&B run: {e}")

    def get_run_url(self) -> Optional[str]:
        """Get W&B run URL"""
        if self.is_initialized and self.run:
            return self.run.url  # type: ignore
        return None


# Global W&B service instance
wandb_service = WandBService()
