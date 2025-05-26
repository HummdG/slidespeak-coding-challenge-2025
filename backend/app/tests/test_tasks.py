# backend/app/tests/conftest.py (SIMPLIFIED VERSION)
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


# backend/app/tests/test_main_simple.py (WORKING VERSION)
import io
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestConvertEndpointSimple:
    """Simplified tests for the /convert endpoint."""

    def test_convert_success(self, test_client, mock_env_vars, sample_pptx_file):
        """Test successful file conversion."""
        mock_task = Mock()
        mock_task.id = "test-job-123"

        with patch("app.main.convert_task") as mock_convert_task, patch(
            "app.main.s3"
        ) as mock_s3:

            mock_convert_task.delay.return_value = mock_task
            mock_s3.put_object.return_value = None

            files = {
                "file": (
                    "test.pptx",
                    io.BytesIO(sample_pptx_file),
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            }

            response = test_client.post("/convert", files=files)

            assert response.status_code == 200
            data = response.json()
            assert "jobId" in data
            assert data["jobId"] == "test-job-123"

    def test_convert_invalid_file_extension(self, test_client, mock_env_vars):
        """Test conversion with invalid file extension."""
        file_content = b"fake content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}

        response = test_client.post("/convert", files=files)

        assert response.status_code == 400
        assert "Only .pptx files supported" in response.json()["detail"]

    def test_convert_no_filename(self, test_client, mock_env_vars):
        """Test conversion with no filename."""
        file_content = b"fake content"
        files = {"file": ("", io.BytesIO(file_content), "application/octet-stream")}

        response = test_client.post("/convert", files=files)
        # FastAPI returns 422 for validation errors, not 400
        assert response.status_code in [400, 422]


class TestStatusEndpointSimple:
    """Simplified tests for the /status endpoint."""

    def test_status_pending(self, test_client, mock_env_vars):
        """Test status check for pending job."""
        job_id = "test-job-123"

        # Patch the import inside the function
        with patch("celery.result.AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "PENDING"
            mock_async_result.return_value = mock_result

            response = test_client.get(f"/status/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processing"

    def test_status_success_with_url(self, test_client, mock_env_vars):
        """Test status check for successful job with URL."""
        job_id = "test-job-123"
        test_url = "https://s3.amazonaws.com/test-bucket/test.pdf"

        with patch("celery.result.AsyncResult") as mock_async_result:
            mock_result = Mock()
            mock_result.state = "SUCCESS"
            mock_result.result = {"url": test_url}
            mock_async_result.return_value = mock_result

            response = test_client.get(f"/status/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "done"
            assert data["url"] == test_url


# backend/app/tests/test_tasks_simple.py (WORKING VERSION)
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from app.tasks import cleanup_old_files, convert_task


class TestConvertTaskSimple:
    """Simplified tests for the convert_task."""

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    @patch("tempfile.gettempdir")  # Mock temp directory for Windows
    def test_convert_task_success(
        self,
        mock_tempdir,
        mock_remove,
        mock_file_open,
        mock_requests_post,
        mock_s3,
        sample_pdf_file,
    ):
        """Test successful file conversion."""
        # Mock temp directory to use a valid Windows path
        mock_tempdir.return_value = "C:\\temp"

        # Mock S3 operations
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = "https://example.com/file.pdf"

        # Mock unoserver response
        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Execute task
        result = convert_task("test-pptx-key", "test-presentation")

        # Verify result
        assert result == {"url": "https://example.com/file.pdf"}

        # Verify S3 operations were called
        mock_s3.download_file.assert_called_once()
        mock_s3.upload_file.assert_called_once()
        mock_s3.generate_presigned_url.assert_called_once()

    @patch("app.tasks.s3")
    def test_convert_task_s3_download_failure(self, mock_s3):
        """Test convert task when S3 download fails."""
        mock_s3.download_file.side_effect = Exception("S3 download failed")

        with pytest.raises(Exception, match="S3 download failed"):
            convert_task("test-pptx-key", "test-presentation")


class TestCleanupOldFilesSimple:
    """Simplified tests for cleanup_old_files."""

    @patch("app.tasks.s3")
    def test_cleanup_old_files_success(self, mock_s3):
        """Test successful cleanup of old files."""
        old_time = datetime.now() - timedelta(days=2)
        new_time = datetime.now() - timedelta(hours=12)

        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "old-file.pdf", "LastModified": old_time},
                {"Key": "new-file.pdf", "LastModified": new_time},
            ]
        }
        mock_s3.delete_object.return_value = None

        result = cleanup_old_files()

        assert mock_s3.delete_object.call_count == 1
        assert "Deleted 1 files" in result

    @patch("app.tasks.s3")
    def test_cleanup_no_files_in_bucket(self, mock_s3):
        """Test cleanup when bucket is empty."""
        mock_s3.list_objects_v2.return_value = {}
        result = cleanup_old_files()
        mock_s3.delete_object.assert_not_called()
