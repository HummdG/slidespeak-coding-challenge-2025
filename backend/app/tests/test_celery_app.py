import os
from unittest.mock import patch

from app.celery_app import celery


class TestCeleryConfiguration:
    """Test Celery app configuration."""

    def test_celery_app_name(self):
        """Test Celery app name is set correctly."""
        assert celery.main == "ppt2pdf"

    def test_celery_task_serialization(self):
        """Test task serialization settings."""
        assert celery.conf.task_serializer == "json"
        assert celery.conf.result_serializer == "json"
        assert "json" in celery.conf.accept_content

    def test_celery_timezone_settings(self):
        """Test timezone configuration."""
        assert celery.conf.timezone == "UTC"
        assert celery.conf.enable_utc is True

    def test_celery_time_limits(self):
        """Test task time limit configuration."""
        assert celery.conf.task_soft_time_limit == 300
        assert celery.conf.task_time_limit == 360

    def test_celery_beat_schedule(self):
        """Test Celery beat schedule configuration."""
        schedule = celery.conf.beat_schedule
        assert "cleanup-old-files" in schedule
        cleanup_task = schedule["cleanup-old-files"]
        assert cleanup_task["task"] == "tasks.cleanup_old_files"
        assert cleanup_task["schedule"] == 21600.0

    def test_celery_includes_tasks(self):
        """Test that tasks module is included."""
        assert "tasks" in celery.conf.include
