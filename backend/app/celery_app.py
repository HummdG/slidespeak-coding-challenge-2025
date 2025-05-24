# backend/app/celery_app.py

import os
from celery import Celery

# Instantiate Celery
celery = Celery(
    "ppt2pdf",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://redis:6379/1")),
    include=["tasks"],  # explicitly register tasks.py
)

# Configuration
celery.conf.update(
    # Use JSON serialization to avoid pickle security issues
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone settings
    timezone="UTC",
    enable_utc=True,

    # Task time limits (in seconds)
    task_soft_time_limit=int(os.getenv("TASK_SOFT_TIME_LIMIT", 300)),  # e.g. 5 minutes
    task_time_limit=int(os.getenv("TASK_TIME_LIMIT", 360)),            # e.g. 6 minutes
)
