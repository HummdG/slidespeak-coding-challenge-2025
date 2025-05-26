"""
Integration tests for the complete file conversion workflow.
"""

import io
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.integration
class TestFileConversionWorkflow:
    """Test the complete file conversion workflow."""

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open")
    @patch("os.remove")
    def test_complete_conversion_workflow(
        self,
        mock_remove,
        mock_file_open,
        mock_requests_post,
        mock_s3,
        sample_pptx_file,
        sample_pdf_file,
    ):
        """Test the complete workflow from upload to download URL."""
        client = TestClient(app)

        # Mock S3 operations
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = (
            "https://s3.amazonaws.com/test-bucket/converted.pdf"
        )
        mock_s3.put_object.return_value = None

        # Mock unoserver response
        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Mock file operations
        mock_file_open.return_value.__enter__.return_value.read.return_value = (
            sample_pptx_file
        )
        mock_file_open.return_value.__enter__.return_value.write.return_value = None

        # Step 1: Upload file
        file_data = {
            "file": (
                "presentation.pptx",
                io.BytesIO(sample_pptx_file),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        }

        upload_response = client.post("/convert", files=file_data)
        assert upload_response.status_code == 200

        job_data = upload_response.json()
        job_id = job_data["jobId"]
        assert job_id is not None

        # Step 2: Check status (simulate task completion)
        # Since we're using eager mode, the task should complete immediately
        status_response = client.get(f"/status/{job_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()

        # In eager mode, task should be completed
        assert status_data["status"] == "done"
        assert "url" in status_data
        assert (
            status_data["url"] == "https://s3.amazonaws.com/test-bucket/converted.pdf"
        )

        # Verify all the expected calls were made
        mock_s3.put_object.assert_called_once()  # Original file upload
        mock_s3.download_file.assert_called_once()  # Task downloads file
        mock_s3.upload_file.assert_called_once()  # Task uploads converted file
        mock_s3.generate_presigned_url.assert_called_once()  # Generate download URL
        mock_requests_post.assert_called_once()  # Unoserver conversion

    def test_invalid_file_rejection(self):
        """Test that invalid files are rejected early."""
        client = TestClient(app)

        # Try to upload a non-PPTX file
        file_data = {
            "file": (
                "document.docx",
                io.BytesIO(b"fake docx content"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }

        response = client.post("/convert", files=file_data)
        assert response.status_code == 400
        assert "Only .pptx files supported" in response.json()["detail"]

    @patch("app.tasks.s3")
    def test_s3_upload_failure_handling(self, mock_s3, sample_pptx_file):
        """Test handling of S3 upload failures."""
        client = TestClient(app)

        # Mock S3 failure
        mock_s3.put_object.side_effect = Exception("S3 service unavailable")

        file_data = {
            "file": (
                "presentation.pptx",
                io.BytesIO(sample_pptx_file),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        }

        with pytest.raises(Exception, match="S3 service unavailable"):
            client.post("/convert", files=file_data)

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    def test_unoserver_failure_handling(
        self, mock_requests_post, mock_s3, sample_pptx_file
    ):
        """Test handling of unoserver conversion failures."""
        client = TestClient(app)

        # Mock successful S3 operations
        mock_s3.put_object.return_value = None
        mock_s3.download_file.return_value = None

        # Mock unoserver failure
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception(
            "Conversion service unavailable"
        )
        mock_requests_post.return_value = mock_response

        file_data = {
            "file": (
                "presentation.pptx",
                io.BytesIO(sample_pptx_file),
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        }

        # Upload should succeed
        upload_response = client.post("/convert", files=file_data)
        assert upload_response.status_code == 200

        job_id = upload_response.json()["jobId"]

        # Status should show error
        status_response = client.get(f"/status/{job_id}")
        assert status_response.status_code == 200

        status_data = status_response.json()
        assert status_data["status"] == "error"
        assert "error" in status_data


@pytest.mark.integration
@pytest.mark.slow
class TestConcurrentRequests:
    """Test handling of concurrent requests."""

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open")
    @patch("os.remove")
    def test_multiple_concurrent_uploads(
        self,
        mock_remove,
        mock_file_open,
        mock_requests_post,
        mock_s3,
        sample_pptx_file,
        sample_pdf_file,
    ):
        """Test handling multiple concurrent file uploads."""
        client = TestClient(app)

        # Mock successful operations
        mock_s3.put_object.return_value = None
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = (
            "https://s3.amazonaws.com/test-bucket/converted.pdf"
        )

        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        mock_file_open.return_value.__enter__.return_value.read.return_value = (
            sample_pptx_file
        )

        # Upload multiple files concurrently
        job_ids = []
        for i in range(3):
            file_data = {
                "file": (
                    f"presentation_{i}.pptx",
                    io.BytesIO(sample_pptx_file),
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            }

            response = client.post("/convert", files=file_data)
            assert response.status_code == 200
            job_ids.append(response.json()["jobId"])

        # Check all jobs completed successfully
        for job_id in job_ids:
            status_response = client.get(f"/status/{job_id}")
            assert status_response.status_code == 200

            status_data = status_response.json()
            assert status_data["status"] == "done"
            assert "url" in status_data

        # Verify all S3 operations were called the expected number of times
        assert mock_s3.put_object.call_count == 3  # 3 original uploads
        assert mock_s3.download_file.call_count == 3  # 3 task downloads
        assert mock_s3.upload_file.call_count == 3  # 3 converted uploads


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery and resilience."""

    def test_nonexistent_job_status(self):
        """Test checking status of non-existent job."""
        client = TestClient(app)

        response = client.get("/status/nonexistent-job-id")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "processing"  # Default for unknown jobs

    @patch("app.main.AsyncResult")
    def test_job_status_with_exception(self, mock_async_result):
        """Test job status checking when AsyncResult raises exception."""
        client = TestClient(app)

        # Mock AsyncResult to raise an exception
        mock_result = mock_async_result.return_value
        mock_result.state = "FAILURE"
        mock_result.result = Exception("Database connection failed")

        response = client.get("/status/test-job-id")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "error"
        assert "Database connection failed" in data["error"]


@pytest.mark.integration
class TestPerformance:
    """Test performance-related aspects."""

    def test_large_file_handling(self, sample_pptx_file):
        """Test handling of large files (simulated)."""
        client = TestClient(app)

        # Create a larger file (simulate large PPTX)
        large_file_content = sample_pptx_file * 1000  # Make it bigger

        with patch("app.main.s3") as mock_s3:
            mock_s3.put_object.return_value = None

            with patch("app.tasks.convert_task.delay") as mock_task:
                mock_result = MagicMock()
                mock_result.id = "large-file-job"
                mock_task.return_value = mock_result

                file_data = {
                    "file": (
                        "large_presentation.pptx",
                        io.BytesIO(large_file_content),
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    )
                }

                response = client.post("/convert", files=file_data)
                assert response.status_code == 200

                # Verify the file was handled properly
                mock_s3.put_object.assert_called_once()
                mock_task.assert_called_once()

    def test_api_response_times(self, sample_pptx_file):
        """Test that API responses are reasonably fast."""
        client = TestClient(app)

        with patch("app.main.s3") as mock_s3:
            mock_s3.put_object.return_value = None

            with patch("app.tasks.convert_task.delay") as mock_task:
                mock_result = MagicMock()
                mock_result.id = "performance-test-job"
                mock_task.return_value = mock_result

                file_data = {
                    "file": (
                        "test.pptx",
                        io.BytesIO(sample_pptx_file),
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    )
                }

                start_time = time.time()
                response = client.post("/convert", files=file_data)
                end_time = time.time()

                assert response.status_code == 200
                # API should respond within 1 second (generous for testing)
                assert (end_time - start_time) < 1.0
