import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
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
            "UNOSERVER_HOST": "test-unoserver",
            "UNOSERVER_PORT": "2004",
        },
    ):
        yield


@pytest.fixture
def sample_pptx_file():
    """Create a sample PPTX file for testing."""
    content = b"PK\x03\x04\x14\x00\x06\x00\x08\x00!\x00" + b"A" * 1000
    return content


@pytest.fixture
def sample_pdf_file():
    """Sample PDF content for testing."""
    return b"%PDF-1.4\n%Test PDF content\n" + b"A" * 500
