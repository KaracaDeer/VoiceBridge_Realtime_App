"""
Celery application for background audio processing tasks.
"""
import logging

from celery import Celery

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "voicebridge",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks.transcription_tasks"],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Tasks will be imported automatically by Celery

if __name__ == "__main__":
    celery_app.start()
