"""
Tests for Celery tasks.
"""

import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

from app.tasks import cleanup_old_files, convert_task


class TestConvertTask:
    """Test the convert_task Celery task."""

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    def test_convert_task_success(
        self, mock_remove, mock_file_open, mock_requests_post, mock_s3, sample_pdf_file
    ):
        """Test successful file conversion."""
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

        # Verify S3 operations
        mock_s3.download_file.assert_called_once()
        mock_s3.upload_file.assert_called_once()
        mock_s3.generate_presigned_url.assert_called_once()

        # Verify unoserver call
        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        assert "http://test-unoserver:2004/request" in args
        assert "files" in kwargs
        assert kwargs["data"]["convert-to"] == "pdf"
        assert kwargs["timeout"] == 300

        # Verify cleanup
        assert mock_remove.call_count == 2  # Both temp files removed

    @patch("app.tasks.s3")
    def test_convert_task_s3_download_failure(self, mock_s3):
        """Test convert task when S3 download fails."""
        mock_s3.download_file.side_effect = Exception("S3 download failed")

        with pytest.raises(Exception, match="S3 download failed"):
            convert_task("test-pptx-key", "test-presentation")

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    def test_convert_task_unoserver_failure(self, mock_requests_post, mock_s3):
        """Test convert task when unoserver request fails."""
        mock_s3.download_file.return_value = None

        # Mock unoserver failure
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "Conversion failed"
        )
        mock_requests_post.return_value = mock_response

        with pytest.raises(requests.HTTPError, match="Conversion failed"):
            convert_task("test-pptx-key", "test-presentation")

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_task_s3_upload_failure(
        self, mock_file_open, mock_requests_post, mock_s3, sample_pdf_file
    ):
        """Test convert task when S3 upload fails."""
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.side_effect = Exception("S3 upload failed")

        # Mock unoserver response
        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        with pytest.raises(Exception, match="S3 upload failed"):
            convert_task("test-pptx-key", "test-presentation")

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.remove")
    def test_convert_task_cleanup_on_success(
        self, mock_remove, mock_file_open, mock_requests_post, mock_s3, sample_pdf_file
    ):
        """Test that temporary files are cleaned up on success."""
        # Setup mocks for successful execution
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = "https://example.com/file.pdf"

        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Execute task
        convert_task("test-pptx-key", "test-presentation")

        # Verify cleanup happened
        assert mock_remove.call_count == 2
        removed_files = [call[0][0] for call in mock_remove.call_args_list]
        assert any(".pptx" in f for f in removed_files)
        assert any(".pdf" in f for f in removed_files)

    @patch("app.tasks.s3")
    @patch("app.tasks.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_convert_task_presigned_url_generation(
        self, mock_file_open, mock_requests_post, mock_s3, sample_pdf_file
    ):
        """Test presigned URL generation with correct parameters."""
        # Setup mocks
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = "https://example.com/file.pdf"

        mock_response = MagicMock()
        mock_response.content = sample_pdf_file
        mock_response.raise_for_status.return_value = None
        mock_requests_post.return_value = mock_response

        # Execute task
        convert_task("test-pptx-key", "My Presentation")

        # Verify presigned URL generation
        mock_s3.generate_presigned_url.assert_called_once()
        args, kwargs = mock_s3.generate_presigned_url.call_args

        assert args[0] == "get_object"
        assert kwargs["ExpiresIn"] == 3600
        assert "Bucket" in kwargs["Params"]
        assert "Key" in kwargs["Params"]
        assert "ResponseContentDisposition" in kwargs["Params"]
        assert (
            'filename="My Presentation.pdf"'
            in kwargs["Params"]["ResponseContentDisposition"]
        )


class TestCleanupOldFiles:
    """Test the cleanup_old_files Celery task."""

    @patch("app.tasks.s3")
    def test_cleanup_old_files_success(self, mock_s3):
        """Test successful cleanup of old files."""
        # Mock S3 list response with old and new files
        old_time = datetime.now() - timedelta(days=2)
        new_time = datetime.now() - timedelta(hours=12)

        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "old-file.pdf", "LastModified": old_time},
                {"Key": "new-file.pdf", "LastModified": new_time},
                {"Key": "very-old-file.pptx", "LastModified": old_time},
            ]
        }
        mock_s3.delete_object.return_value = None

        result = cleanup_old_files()

        # Verify correct files were deleted
        assert mock_s3.delete_object.call_count == 2
        deleted_keys = [call[1]["Key"] for call in mock_s3.delete_object.call_args_list]
        assert "old-file.pdf" in deleted_keys
        assert "very-old-file.pptx" in deleted_keys
        assert "new-file.pdf" not in deleted_keys

        assert "Deleted 2 files" in result

    @patch("app.tasks.s3")
    def test_cleanup_no_files_in_bucket(self, mock_s3):
        """Test cleanup when bucket is empty."""
        mock_s3.list_objects_v2.return_value = {}

        result = cleanup_old_files()

        # Should not try to delete anything
        mock_s3.delete_object.assert_not_called()
        assert result is None

    @patch("app.tasks.s3")
    def test_cleanup_no_old_files(self, mock_s3):
        """Test cleanup when no files are old enough."""
        # Mock S3 list response with only new files
        new_time = datetime.now() - timedelta(hours=12)

        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "new-file1.pdf", "LastModified": new_time},
                {"Key": "new-file2.pdf", "LastModified": new_time},
            ]
        }

        result = cleanup_old_files()

        # Should not delete anything
        mock_s3.delete_object.assert_not_called()
        assert "Deleted 0 files" in result

    @patch("app.tasks.s3")
    def test_cleanup_s3_error(self, mock_s3):
        """Test cleanup when S3 operations fail."""
        mock_s3.list_objects_v2.side_effect = Exception("S3 connection failed")

        with pytest.raises(Exception, match="S3 connection failed"):
            cleanup_old_files()

    @patch("app.tasks.s3")
    def test_cleanup_delete_error(self, mock_s3):
        """Test cleanup when delete operation fails."""
        old_time = datetime.now() - timedelta(days=2)

        mock_s3.list_objects_v2.return_value = {
            "Contents": [
                {"Key": "old-file.pdf", "LastModified": old_time},
            ]
        }
        mock_s3.delete_object.side_effect = Exception("Delete failed")

        with pytest.raises(Exception, match="Delete failed"):
            cleanup_old_files()


class TestTaskConfiguration:
    """Test task configuration and environment variables."""

    def test_environment_variables_loaded(self):
        """Test that environment variables are properly loaded."""
        from app.tasks import BUCKET, PORT, REGION, UNOSERVER

        assert BUCKET == "test-bucket"
        assert REGION in ["us-east-1", "eu-west-1"]  # Default or test value
        assert UNOSERVER == "test-unoserver"
        assert PORT == "2004"

    @patch.dict(os.environ, {"AWS_S3_BUCKET": "custom-bucket"})
    def test_custom_environment_variables(self):
        """Test that custom environment variables are respected."""
        # Need to reimport to get updated env vars
        import importlib

        from app import tasks

        importlib.reload(tasks)

        assert tasks.BUCKET == "custom-bucket"
