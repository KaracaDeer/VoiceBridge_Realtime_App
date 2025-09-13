"""
Performance monitoring for ML models.
Tracks metrics, accuracy, and system performance.
"""
import logging
import time
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors performance of ML models and transcription pipeline."""

    def __init__(self, max_history: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_history: Maximum number of records to keep in history
        """
        self.max_history = max_history
        
        # Performance metrics
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        
        # Real-time stats
        self.stats = {
            "total_transcriptions": 0,
            "successful_transcriptions": 0,
            "failed_transcriptions": 0,
            "average_processing_time": 0.0,
            "average_confidence": 0.0,
            "models_used": set()
        }
        
        logger.info("PerformanceMonitor initialized")

    async def record_transcription_metrics(self, model_name: str, 
                                         processing_time: float,
                                         confidence: float,
                                         success: bool,
                                         additional_metrics: Optional[Dict[str, Any]] = None):
        """
        Record transcription performance metrics.
        
        Args:
            model_name: Name of the model used
            processing_time: Time taken for processing
            confidence: Confidence score
            success: Whether transcription was successful
            additional_metrics: Additional metrics to record
        """
        try:
            timestamp = time.time()
            
            # Create metrics record
            record = {
                "timestamp": timestamp,
                "model_name": model_name,
                "processing_time": processing_time,
                "confidence": confidence,
                "success": success,
                "additional_metrics": additional_metrics or {}
            }
            
            # Store in history
            self.history[model_name].append(record)
            
            # Update real-time stats
            self._update_stats(model_name, processing_time, confidence, success)
            
            # Update model-specific metrics
            self._update_model_metrics(model_name, record)
            
            logger.debug(f"Recorded metrics for {model_name}: {processing_time:.3f}s, confidence: {confidence:.3f}")
            
        except Exception as e:
            logger.error(f"Error recording metrics: {e}")

    def _update_stats(self, model_name: str, processing_time: float, 
                     confidence: float, success: bool):
        """Update real-time statistics."""
        self.stats["total_transcriptions"] += 1
        self.stats["models_used"].add(model_name)
        
        if success:
            self.stats["successful_transcriptions"] += 1
        else:
            self.stats["failed_transcriptions"] += 1
        
        # Update running averages
        total = self.stats["total_transcriptions"]
        if total > 0:
            # Update average processing time
            current_avg = self.stats["average_processing_time"]
            self.stats["average_processing_time"] = (
                (current_avg * (total - 1) + processing_time) / total
            )
            
            # Update average confidence (only for successful transcriptions)
            if success:
                successful = self.stats["successful_transcriptions"]
                if successful > 0:
                    current_avg_conf = self.stats["average_confidence"]
                    self.stats["average_confidence"] = (
                        (current_avg_conf * (successful - 1) + confidence) / successful
                    )

    def _update_model_metrics(self, model_name: str, record: Dict[str, Any]):
        """Update model-specific metrics."""
        if model_name not in self.metrics:
            self.metrics[model_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_processing_time": 0.0,
                "total_confidence": 0.0,
                "min_processing_time": float('inf'),
                "max_processing_time": 0.0,
                "min_confidence": 1.0,
                "max_confidence": 0.0
            }
        
        metrics = self.metrics[model_name]
        metrics["total_requests"] += 1
        
        if record["success"]:
            metrics["successful_requests"] += 1
            metrics["total_confidence"] += record["confidence"]
            metrics["min_confidence"] = min(metrics["min_confidence"], record["confidence"])
            metrics["max_confidence"] = max(metrics["max_confidence"], record["confidence"])
        else:
            metrics["failed_requests"] += 1
        
        metrics["total_processing_time"] += record["processing_time"]
        metrics["min_processing_time"] = min(metrics["min_processing_time"], record["processing_time"])
        metrics["max_processing_time"] = max(metrics["max_processing_time"], record["processing_time"])

    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics."""
        total = self.stats["total_transcriptions"]
        successful = self.stats["successful_transcriptions"]
        
        return {
            "total_transcriptions": total,
            "successful_transcriptions": successful,
            "failed_transcriptions": self.stats["failed_transcriptions"],
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "average_processing_time": self.stats["average_processing_time"],
            "average_confidence": self.stats["average_confidence"],
            "models_used": list(self.stats["models_used"]),
            "timestamp": time.time()
        }

    def get_model_stats(self, model_name: str) -> Dict[str, Any]:
        """Get performance statistics for a specific model."""
        if model_name not in self.metrics:
            return {"error": f"No metrics found for model {model_name}"}
        
        metrics = self.metrics[model_name]
        total = metrics["total_requests"]
        successful = metrics["successful_requests"]
        
        return {
            "model_name": model_name,
            "total_requests": total,
            "successful_requests": successful,
            "failed_requests": metrics["failed_requests"],
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "average_processing_time": (metrics["total_processing_time"] / total) if total > 0 else 0.0,
            "min_processing_time": metrics["min_processing_time"] if metrics["min_processing_time"] != float('inf') else 0.0,
            "max_processing_time": metrics["max_processing_time"],
            "average_confidence": (metrics["total_confidence"] / successful) if successful > 0 else 0.0,
            "min_confidence": metrics["min_confidence"] if metrics["min_confidence"] != 1.0 else 0.0,
            "max_confidence": metrics["max_confidence"],
            "timestamp": time.time()
        }

    def get_recent_history(self, model_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent performance history for a model.
        
        Args:
            model_name: Name of the model
            limit: Maximum number of records to return
            
        Returns:
            List of recent performance records
        """
        if model_name not in self.history:
            return []
        
        history = list(self.history[model_name])
        return history[-limit:] if limit > 0 else history

    def get_performance_trends(self, model_name: str, window_size: int = 50) -> Dict[str, Any]:
        """
        Get performance trends for a model.
        
        Args:
            model_name: Name of the model
            window_size: Size of the sliding window for trend calculation
            
        Returns:
            Performance trends dictionary
        """
        if model_name not in self.history:
            return {"error": f"No history found for model {model_name}"}
        
        history = list(self.history[model_name])
        if len(history) < window_size:
            return {"error": f"Insufficient data for trend analysis (need {window_size}, have {len(history)})"}
        
        # Calculate trends for recent window
        recent_records = history[-window_size:]
        
        # Processing time trend
        processing_times = [r["processing_time"] for r in recent_records]
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        # Confidence trend
        successful_records = [r for r in recent_records if r["success"]]
        if successful_records:
            confidences = [r["confidence"] for r in successful_records]
            avg_confidence = sum(confidences) / len(confidences)
        else:
            avg_confidence = 0.0
        
        # Success rate trend
        success_count = sum(1 for r in recent_records if r["success"])
        success_rate = (success_count / len(recent_records)) * 100
        
        return {
            "model_name": model_name,
            "window_size": window_size,
            "average_processing_time": avg_processing_time,
            "average_confidence": avg_confidence,
            "success_rate": success_rate,
            "total_requests": len(recent_records),
            "successful_requests": success_count,
            "timestamp": time.time()
        }

    def get_monitor_info(self) -> Dict[str, Any]:
        """Get monitor information and configuration."""
        return {
            "monitor_type": "ml_performance_monitor",
            "max_history": self.max_history,
            "total_models_tracked": len(self.metrics),
            "models_tracked": list(self.metrics.keys()),
            "overall_stats": self.get_overall_stats(),
            "timestamp": time.time()
        }

    def clear_history(self, model_name: Optional[str] = None):
        """
        Clear performance history.
        
        Args:
            model_name: Specific model to clear, or None for all models
        """
        if model_name:
            if model_name in self.history:
                self.history[model_name].clear()
                logger.info(f"Cleared history for model {model_name}")
        else:
            self.history.clear()
            self.metrics.clear()
            self.stats = {
                "total_transcriptions": 0,
                "successful_transcriptions": 0,
                "failed_transcriptions": 0,
                "average_processing_time": 0.0,
                "average_confidence": 0.0,
                "models_used": set()
            }
            logger.info("Cleared all performance history")
