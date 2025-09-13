"""
Monitoring routes for VoiceBridge API
Handles MLFlow, Prometheus, and model monitoring endpoints
"""
# type: ignore
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

# from src.database.mysql_models import User  # Temporarily disabled
from src.services.auth_service import get_current_user
from src.services.mlflow_service import mlflow_service
from src.services.model_monitoring_service import model_monitoring_service
from src.services.prometheus_service import prometheus_metrics
from src.services.wandb_service import wandb_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        # Get system health from Prometheus
        system_health = prometheus_metrics.get_system_health()

        # Get model health
        model_health = model_monitoring_service.get_model_health_status()

        # Combine health information
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_health,
            "models": model_health,
            "overall_status": "healthy",
        }

        # Determine overall status
        if system_health.get("status") == "error" or model_health.get("overall_status") in ["critical", "error"]:
            health_status["overall_status"] = "critical"
        elif system_health.get("status") == "warning" or model_health.get("overall_status") == "warning":
            health_status["overall_status"] = "warning"

        return health_status

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health",
        )


@router.get("/metrics")
async def get_prometheus_metrics():
    """Get Prometheus metrics in text format"""
    try:
        metrics_text = prometheus_metrics.get_metrics()
        return Response(content=metrics_text, media_type="text/plain; version=0.0.4; charset=utf-8")
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics",
        )


@router.get("/metrics/json")
async def get_metrics_json():
    """Get Prometheus metrics in JSON format"""
    try:
        metrics_dict = prometheus_metrics.get_metrics_dict()
        return JSONResponse(content=metrics_dict)
    except Exception as e:
        logger.error(f"Error getting metrics JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics",
        )


@router.get("/mlflow/experiments")
async def get_mlflow_experiments(current_user: User = Depends(get_current_user)):
    """Get MLFlow experiment runs (requires authentication)"""
    try:
        runs = mlflow_service.get_experiment_runs(limit=50)
        return {
            "experiment_name": mlflow_service.experiment_name,
            "total_runs": len(runs),
            "runs": runs,
        }
    except Exception as e:
        logger.error(f"Error getting MLFlow experiments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MLFlow experiments",
        )


@router.get("/mlflow/performance-summary")
async def get_mlflow_performance_summary(
    current_user: User = Depends(get_current_user),
):
    """Get MLFlow performance summary (requires authentication)"""
    try:
        summary = mlflow_service.get_model_performance_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting MLFlow performance summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get performance summary",
        )


@router.get("/models/performance")
async def get_model_performance(model_name: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Get model performance summary (requires authentication)"""
    try:
        summary = model_monitoring_service.get_model_performance_summary(model_name)
        return summary
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model performance",
        )


@router.get("/models/alerts")
async def get_model_alerts(
    model_name: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
):
    """Get model drift alerts (requires authentication)"""
    try:
        alerts = model_monitoring_service.get_drift_alerts(model_name=model_name, severity=severity, hours=hours)
        return {
            "total_alerts": len(alerts),
            "filters": {"model_name": model_name, "severity": severity, "hours": hours},
            "alerts": alerts,
        }
    except Exception as e:
        logger.error(f"Error getting model alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model alerts",
        )


@router.get("/models/health")
async def get_model_health(current_user: User = Depends(get_current_user)):
    """Get model health status (requires authentication)"""
    try:
        health = model_monitoring_service.get_model_health_status()
        return health
    except Exception as e:
        logger.error(f"Error getting model health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model health",
        )


@router.get("/wandb/run-url")
async def get_wandb_run_url(current_user: User = Depends(get_current_user)):
    """Get current W&B run URL (requires authentication)"""
    try:
        run_url = wandb_service.get_run_url()
        if run_url:
            return {"run_url": run_url, "status": "active"}
        else:
            return {"run_url": None, "status": "inactive"}
    except Exception as e:
        logger.error(f"Error getting W&B run URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get W&B run URL",
        )


@router.post("/models/record-performance")
async def record_model_performance(
    model_name: str,
    accuracy: float,
    confidence: float,
    processing_time: float,
    error_occurred: bool = False,
    current_user: User = Depends(get_current_user),
):
    """Record model performance metrics (requires authentication)"""
    try:
        model_monitoring_service.record_model_performance(
            model_name=model_name,
            accuracy=accuracy,
            confidence=confidence,
            processing_time=processing_time,
            error_occurred=error_occurred,
        )

        return {
            "message": "Model performance recorded successfully",
            "model_name": model_name,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error recording model performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record model performance",
        )


@router.get("/system/resources")
async def get_system_resources():
    """Get system resource usage"""
    try:
        import psutil

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory usage
        memory = psutil.virtual_memory()

        # Disk usage
        disk = psutil.disk_usage("/")

        # Network I/O
        network = psutil.net_io_counters()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "status": "normal" if cpu_percent < 80 else "high",
            },
            "memory": {
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "status": "normal" if memory.percent < 80 else "high",
            },
            "disk": {
                "usage_percent": round((disk.used / disk.total) * 100, 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "total_gb": round(disk.total / (1024**3), 2),
                "status": "normal" if (disk.used / disk.total) < 0.9 else "high",
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
        }
    except Exception as e:
        logger.error(f"Error getting system resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system resources",
        )


@router.get("/logs/recent")
async def get_recent_logs(
    lines: int = 100,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get recent application logs (requires authentication)"""
    try:
        # This is a simplified implementation
        # In production, you might want to use a proper log aggregation system
        log_file = "logs/voicebridge.log"

        try:
            with open(log_file, "r") as f:
                all_lines = f.readlines()

            # Get recent lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            # Filter by level if specified
            if level:
                recent_lines = [line for line in recent_lines if level.upper() in line]

            return {
                "total_lines": len(recent_lines),
                "requested_lines": lines,
                "level_filter": level,
                "logs": [line.strip() for line in recent_lines],
            }
        except FileNotFoundError:
            return {"message": "Log file not found", "total_lines": 0, "logs": []}

    except Exception as e:
        logger.error(f"Error getting recent logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent logs",
        )


@router.get("/dashboard/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """Get comprehensive dashboard summary (requires authentication)"""
    try:
        # Get all monitoring data
        system_health = prometheus_metrics.get_system_health()
        model_health = model_monitoring_service.get_model_health_status()
        model_performance = model_monitoring_service.get_model_performance_summary()
        recent_alerts = model_monitoring_service.get_drift_alerts(hours=24)

        # Get system resources
        import psutil

        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "status": system_health.get("status", "unknown"),
            },
            "models": {
                "health_status": model_health.get("overall_status", "unknown"),
                "total_models": len(model_performance),
                "performance_summary": model_performance,
            },
            "alerts": {
                "total_alerts_24h": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a.get("severity") == "critical"]),
                "recent_alerts": recent_alerts[:5],  # Last 5 alerts
            },
            "monitoring": {
                "mlflow_active": mlflow_service.mlflow_uri is not None,
                "wandb_active": wandb_service.is_initialized,
                "prometheus_active": True,
            },
        }

        # Determine overall status
        if system_health.get("status") == "error" or model_health.get("overall_status") in ["critical", "error"]:
            summary["overall_status"] = "critical"
        elif (
            system_health.get("status") == "warning"
            or model_health.get("overall_status") == "warning"
            or (summary.get("alerts") or {}).get("critical_alerts", 0) > 0
        ):
            summary["overall_status"] = "warning"

        return summary

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard summary",
        )
