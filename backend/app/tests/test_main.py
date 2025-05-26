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
