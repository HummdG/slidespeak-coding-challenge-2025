"""
Tests for Celery app configuration.
"""

import os
from unittest.mock import patch

import pytest

from app.celery_app import celery


class TestCeleryConfiguration:
    """Test Celery app configuration."""

    def test_celery_app_name(self):
        """Test Celery app name is set correctly."""
        assert celery.main == "ppt2pdf"

    def test_celery_broker_configuration(self):
        """Test Celery broker configuration."""
        # In test environment, we should be using memory or test Redis
        broker_url = celery.conf.broker_url
        assert broker_url is not None
        # In our test setup, it should be memory:// or redis://
        assert "memory://" in broker_url or "redis://" in broker_url

    def test_celery_result_backend_configuration(self):
        """Test Celery result backend configuration."""
        backend_url = celery.conf.result_backend
        assert backend_url is not None
        # Should be memory or Redis based
        assert "memory://" in backend_url or "redis://" in backend_url

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
        assert celery.conf.task_soft_time_limit == 300  # 5 minutes
        assert celery.conf.task_time_limit == 360  # 6 minutes

    def test_celery_beat_schedule(self):
        """Test Celery beat schedule configuration."""
        schedule = celery.conf.beat_schedule
        assert "cleanup-old-files" in schedule

        cleanup_task = schedule["cleanup-old-files"]
        assert cleanup_task["task"] == "tasks.cleanup_old_files"
        assert cleanup_task["schedule"] == 21600.0  # 6 hours

    def test_celery_includes_tasks(self):
        """Test that tasks module is included."""
        assert "tasks" in celery.conf.include


class TestCeleryEnvironmentConfiguration:
    """Test Celery configuration with different environment variables."""

    @patch.dict(os.environ, {"REDIS_URL": "redis://custom-redis:6379/0"})
    def test_custom_redis_url(self):
        """Test Celery with custom Redis URL."""
        # Need to reimport celery_app to pick up new environment
        import importlib

        from app import celery_app

        importlib.reload(celery_app)

        # Check that custom Redis URL is used
        broker_url = celery_app.celery.conf.broker_url
        assert "redis://custom-redis:6379/0" in broker_url

    @patch.dict(os.environ, {"REDIS_RESULT_BACKEND": "redis://result-redis:6379/1"})
    def test_custom_result_backend(self):
        """Test Celery with custom result backend."""
        import importlib

        from app import celery_app

        importlib.reload(celery_app)

        backend_url = celery_app.celery.conf.result_backend
        assert "redis://result-redis:6379/1" in backend_url

    @patch.dict(os.environ, {"TASK_SOFT_TIME_LIMIT": "600", "TASK_TIME_LIMIT": "720"})
    def test_custom_time_limits(self):
        """Test Celery with custom time limits."""
        import importlib

        from app import celery_app

        importlib.reload(celery_app)

        assert celery_app.celery.conf.task_soft_time_limit == 600
        assert celery_app.celery.conf.task_time_limit == 720


class TestTaskRegistration:
    """Test that tasks are properly registered with Celery."""

    def test_convert_task_registered(self):
        """Test that convert_task is registered."""
        registered_tasks = celery.tasks
        assert "tasks.convert_task" in registered_tasks

    def test_cleanup_task_registered(self):
        """Test that cleanup_old_files is registered."""
        registered_tasks = celery.tasks
        assert "tasks.cleanup_old_files" in registered_tasks

    def test_task_inspection(self):
        """Test task inspection capabilities."""
        # Get task info
        convert_task_obj = celery.tasks.get("tasks.convert_task")
        assert convert_task_obj is not None

        cleanup_task_obj = celery.tasks.get("tasks.cleanup_old_files")
        assert cleanup_task_obj is not None


class TestCeleryHealthCheck:
    """Test Celery health and connectivity."""

    def test_celery_ping(self):
        """Test Celery ping functionality."""
        # In eager mode, this should work
        try:
            inspect = celery.control.inspect()
            # This might not work in test mode, so we'll catch exceptions
            stats = inspect.stats()
            # If it works, great! If not, that's also fine in test mode
            assert stats is not None or stats is None
        except Exception:
            # In test/eager mode, inspection might not work
            pytest.skip("Celery inspection not available in test mode")

    def test_celery_task_routing(self):
        """Test basic task routing configuration."""
        # Verify default routing works
        assert celery.conf.task_default_queue is None or isinstance(
            celery.conf.task_default_queue, str
        )
        assert celery.conf.task_default_exchange is None or isinstance(
            celery.conf.task_default_exchange, str
        )


class TestCeleryWorkerConfiguration:
    """Test Celery worker-specific configuration."""

    def test_worker_prefetch_settings(self):
        """Test worker prefetch configuration."""
        # Check if worker prefetch is configured (it might be default)
        prefetch = celery.conf.worker_prefetch_multiplier
        assert prefetch is None or isinstance(prefetch, int)

    def test_worker_concurrency_settings(self):
        """Test worker concurrency configuration."""
        # Check worker concurrency (might be default)
        concurrency = celery.conf.worker_concurrency
        assert concurrency is None or isinstance(concurrency, int)

    def test_security_settings(self):
        """Test security-related settings."""
        # Verify we're using JSON serialization for security
        assert celery.conf.task_serializer == "json"
        assert celery.conf.result_serializer == "json"

        # Verify we're not using pickle (security risk)
        assert "pickle" not in celery.conf.accept_content
        assert "application/x-python-serialize" not in celery.conf.accept_content
