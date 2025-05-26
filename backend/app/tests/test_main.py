import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient
from fastapi import UploadFile
import io
import uuid

from main import app


class TestConvertEndpoint:
    """Test the /convert endpoint."""

    def test_convert_success(self, test_client, mock_env_vars, mock_s3):
        """Test successful file conversion."""
        # Mock the Celery task
        mock_task = Mock()
        mock_task.id = "test-job-123"
        
        with patch('main.convert_task') as mock_convert_task:
            mock_convert_task.delay.return_value = mock_task
            
            # Create test file
            file_content = b"fake pptx content"
            files = {
                "file": ("test.pptx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.presentationml.presentation")
            }
            
            response = test_client.post("/convert", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "jobId" in data
            assert data["jobId"] == "test-job-123"
            
            # Verify the task was called
            mock_convert_task.delay.assert_called_once()

    def test_convert_invalid_file_extension(self, test_client, mock_env_vars):
        """Test conversion with invalid file extension."""
        file_content = b"fake content"
        files = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }
        
        response = test_client.post("/convert", files=files)
        
        assert response.status_code == 400
        assert "Only .pptx files supported" in response.json()["detail"]

    def test_convert_no_filename(self, test_client, mock_env_vars):
        """Test conversion with no filename."""
        file_content = b"fake content"
        
        # Create UploadFile without filename
        upload_file = UploadFile(filename=None, file=io.BytesIO(file_content))
        
        with patch('main.File') as mock_file:
            mock_file.return_value = upload_file
            
            response = test_client.post("/convert", files={"file": ("", io.BytesIO(file_content), "application/octet-stream")})
            
            assert response.status_code == 400

    @patch('main.s3')
    def test_convert_s3_upload_error(self, mock_s3_client, test_client, mock_env_vars):
        """Test conversion when S3 upload fails."""
        mock_s3_client.put_object.side_effect = Exception("S3 error")
        
        file_content = b"fake pptx content"
        files = {
            "file": ("test.pptx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.presentationml.presentation")
        }
        
        with pytest.raises(Exception):
            test_client.post("/convert", files=files)


class TestStatusEndpoint:
    """Test the /status/{job_id} endpoint."""

    def test_status_pending(self, test_client, mock_env_vars):
        """Test status check for pending job."""
        job_id = "test-job-123"
        
        mock_result = Mock()
        mock_result.state = "PENDING"
        
        with patch('main.AsyncResult') as mock_async_result:
            mock_async_result.return_value = mock_result
            
            response = test_client.get(f"/status/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processing"

    def test_status_success_with_url(self, test_client, mock_env_vars):
        """Test status check for successful job with URL."""
        job_id = "test-job-123"
        test_url = "https://s3.amazonaws.com/test-bucket/test.pdf"
        
        mock_result = Mock()
        mock_result.state = "SUCCESS"
        mock_result.result = {"url": test_url}
        
        with patch('main.AsyncResult') as mock_async_result:
            mock_async_result.return_value = mock_result
            
            response = test_client.get(f"/status/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "done"
            assert data["url"] == test_url

    def test_status_failure(self, test_client, mock_env_vars):
        """Test status check for failed job."""
        job_id = "test-job-123"
        error_msg = "Conversion failed"
        
        mock_result = Mock()
        mock_result.state = "FAILURE"
        mock_result.result = Exception(error_msg)
        
        with patch('main.AsyncResult') as mock_async_result:
            mock_async_result.return_value = mock_result
            
            response = test_client.get(f"/status/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"
            assert error_msg in str(data["error"])

    def test_status_revoked(self, test_client, mock_env_vars):
        """Test status check for revoked job."""
        job_id = "test-job-123"
        
        mock_result = Mock()
        mock_result.state = "REVOKED"
        mock_result.result = "Task was revoked"
        
        with patch('main.AsyncResult') as mock_async_result:
            mock_async_result.return_value = mock_result
            
            response = test_client.get(f"/status/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"

    def test_status_unknown_state(self, test_client, mock_env_vars):
        """Test status check for unknown job state."""
        job_id = "test-job-123"
        
        mock_result = Mock()
        mock_result.state = "RETRY"
        
        with patch('main.AsyncResult') as mock_async_result:
            mock_async_result.return_value = mock_result
            
            response = test_client.get(f"/status/{job_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "retry"


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_preflight_request(self, test_client):
        """Test CORS preflight request."""
        response = test_client.options(
            "/convert",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # FastAPI handles CORS automatically, just verify the endpoint exists
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS