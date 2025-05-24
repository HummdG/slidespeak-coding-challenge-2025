from celery import Celery
import os

celery = Celery(
    "ppt2pdf",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/1")
)

# Optional: task time limits
celery.conf.update(
    task_soft_time_limit=300,  # abort tasks >5min
    task_time_limit=360
)
