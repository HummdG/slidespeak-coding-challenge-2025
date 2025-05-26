import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import boto3
import fakeredis
import pytest
from celery import Celery
from fastapi.testclient import TestClient
from moto import mock_s3

from celery_app import celery

# Import your app modules
from main import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "AWS_S3_BUCKET": "test-bucket",
            "AWS_REGION": "us-east-1",
            "REDIS_URL": "redis://localhost:6379/0",
            "UNOSERVER_HOST": "localhost",
            "UNOSERVER_PORT": "2004",
        },
    ):
        yield


@pytest.fixture
def mock_s3():
    """Mock S3 service."""
    with mock_s3():
        # Create the mock S3 client and bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        yield s3_client


@pytest.fixture
def mock_redis():
    """Mock Redis connection."""
    fake_redis = fakeredis.FakeRedis()
    with patch("redis.Redis", return_value=fake_redis):
        yield fake_redis


@pytest.fixture
def mock_celery_app():
    """Mock Celery app for testing."""
    test_celery = Celery("test", broker="memory://")
    test_celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        result_backend="cache+memory://",
    )
    return test_celery


@pytest.fixture
def sample_pptx_file():
    """Create a sample PPTX file for testing."""
    # Create a minimal valid PPTX-like file structure
    content = b"PK\x03\x04\x14\x00\x06\x00\x08\x00!\x00" + b"A" * 100
    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
        f.write(content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    return b"%PDF-1.4\n%Test PDF content\n" + b"A" * 100


@pytest.fixture
def mock_unoserver_response(sample_pdf_content):
    """Mock unoserver API response."""
    mock_response = Mock()
    mock_response.content = sample_pdf_content
    mock_response.raise_for_status = Mock()
    return mock_response
