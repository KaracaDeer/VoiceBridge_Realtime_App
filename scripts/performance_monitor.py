#!/usr/bin/env python3
"""
Performance monitoring script for VoiceBridge.
Monitors system performance and generates reports.
"""
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor system performance metrics."""

    def __init__(self):
        self.metrics = []

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB

            # Network metrics
            network = psutil.net_io_counters()

            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {"percent": cpu_percent, "count": cpu_count},
                "memory": {"percent": memory_percent, "available_gb": round(memory_available, 2)},
                "disk": {"percent": disk_percent, "free_gb": round(disk_free, 2)},
                "network": {"bytes_sent": network.bytes_sent, "bytes_recv": network.bytes_recv},
            }

            return metrics

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {}

    def monitor_application(self, duration_minutes: int = 5):
        """Monitor application performance for specified duration."""
        logger.info(f"Starting performance monitoring for {duration_minutes} minutes...")

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            metrics = self.collect_system_metrics()
            if metrics:
                self.metrics.append(metrics)
                logger.info(
                    f"CPU: {metrics['cpu']['percent']}%, "
                    f"Memory: {metrics['memory']['percent']}%, "
                    f"Disk: {metrics['disk']['percent']}%"
                )

            time.sleep(30)  # Collect metrics every 30 seconds

        self.generate_report()

    def generate_report(self):
        """Generate performance report."""
        if not self.metrics:
            logger.warning("No metrics collected")
            return

        # Calculate averages
        cpu_avg = sum(m["cpu"]["percent"] for m in self.metrics) / len(self.metrics)
        memory_avg = sum(m["memory"]["percent"] for m in self.metrics) / len(self.metrics)
        disk_avg = sum(m["disk"]["percent"] for m in self.metrics) / len(self.metrics)

        report = {
            "monitoring_duration": f"{len(self.metrics) * 30} seconds",
            "samples_collected": len(self.metrics),
            "averages": {
                "cpu_percent": round(cpu_avg, 2),
                "memory_percent": round(memory_avg, 2),
                "disk_percent": round(disk_avg, 2),
            },
            "peak_values": {
                "cpu_percent": max(m["cpu"]["percent"] for m in self.metrics),
                "memory_percent": max(m["memory"]["percent"] for m in self.metrics),
                "disk_percent": max(m["disk"]["percent"] for m in self.metrics),
            },
            "detailed_metrics": self.metrics,
        }

        # Save report
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Performance report saved to {filename}")
        logger.info(f"Average CPU: {cpu_avg:.2f}%, Memory: {memory_avg:.2f}%, Disk: {disk_avg:.2f}%")


def main():
    """Main function."""
    monitor = PerformanceMonitor()

    try:
        # Monitor for 5 minutes
        monitor.monitor_application(duration_minutes=5)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        monitor.generate_report()


if __name__ == "__main__":
    main()
