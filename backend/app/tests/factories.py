"""
Test data factories for generating test data.
"""
import io
import zipfile
from datetime import datetime, timedelta
from typing import Dict, List

import factory


class FileFactory:
    """Factory for creating test files."""

    @staticmethod
    def create_pptx_file(filename: str = "test.pptx", size_kb: int = 100) -> bytes:
        """Create a minimal valid PPTX file."""
        # Create a minimal ZIP structure that mimics a PPTX file
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add minimal PPTX structure
            zip_file.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-presentationml.presentation.main+xml"/>
</Types>""")
            
            zip_file.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""")
            
            zip_file.writestr("ppt/presentation.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldMasterIdLst/>
    <p:sldIdLst/>
    <p:sldSz cx="9144000" cy="6858000" type="screen4x3"/>
    <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""")
            
            # Add padding to reach desired size
            padding_size = max(0, (size_kb * 1024) - buffer.tell())
            if padding_size > 0:
                zip_file.writestr("padding.txt", "x" * padding_size)
        
        content = buffer.getvalue()
        buffer.close()
        return content

    @staticmethod
    def create_pdf_file(filename: str = "test.pdf", size_kb: int = 50) -> bytes:
        """Create a minimal valid PDF file."""
        # Create minimal PDF structure
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj

xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
199
%%EOF"""
        
        # Add padding to reach desired size
        padding_size = max(0, (size_kb * 1024) - len(pdf_content))
        if padding_size > 0:
            pdf_content += b"\n" + b"%" + b"x" * (padding_size - 2)
        
        return pdf_content

    @staticmethod
    def create_invalid_file(filename: str, content: str = "This is not a valid PPTX file") -> bytes:
        """Create an invalid file for testing error cases."""
        return content.encode('utf-8')


class S3ObjectFactory:
    """Factory for creating S3 object data for testing."""

    @staticmethod
    def create_s3_object_list(count: int = 3, old_count: int = 1) -> Dict:
        """Create a list of S3 objects with some old and some new."""
        objects = []
        
        # Create old objects
        for i in range(old_count):
            old_time = datetime.now() - timedelta(days=2 + i)
            objects.append({
                "Key": f"old-file-{i}.pdf",
                "LastModified": old_time,
                "Size": 1024 * (i + 1)
            })
        
        # Create new objects
        for i in range(count - old_count):
            new_time = datetime.now() - timedelta(hours=12 + i)
            objects.append({
                "Key": f"new-file-{i}.pdf",
                "LastModified": new_time,
                "Size": 2048 * (i + 1)
            })
        
        return {"Contents": objects}

    @staticmethod
    def create_empty_bucket() -> Dict:
        """Create an empty S3 bucket response."""
        return {}


class TaskResultFactory:
    """Factory for creating Celery task results."""

    @staticmethod
    def create_success_result(url: str = "https://example.com/file.pdf") -> Dict:
        """Create a successful task result."""
        return {"url": url}

    @staticmethod
    def create_error_result(error_message: str = "Conversion failed") -> Exception:
        """Create an error result."""
        return Exception(error_message)


class APIResponseFactory:
    """Factory for creating API response data."""

    @staticmethod
    def create_upload_response(job_id: str = "test-job-123") -> Dict:
        """Create a successful upload response."""
        return {"jobId": job_id}

    @staticmethod
    def create_status_response(status: str, **kwargs) -> Dict:
        """Create a status response."""
        response = {"status": status}
        response.update(kwargs)
        return response

    @staticmethod
    def create_error_response(error_message: str) -> Dict:
        """Create an error response."""
        return {"detail": error_message}


class UnoserverResponseFactory:
    """Factory for creating Unoserver response mocks."""

    @staticmethod
    def create_success_response(pdf_content: bytes = None) -> Dict:
        """Create a successful Unoserver response."""
        if pdf_content is None:
            pdf_content = FileFactory.create_pdf_file()
        
        return {
            "status_code": 200,
            "content": pdf_content,
            "headers": {"Content-Type": "application/pdf"}
        }

    @staticmethod
    def create_error_response(status_code: int = 500, error_message: str = "Internal Server Error") -> Dict:
        """Create an error Unoserver response."""
        return {
            "status_code": status_code,
            "content": error_message.encode(),
            "headers": {"Content-Type": "text/plain"}
        }


class TestScenarioFactory:
    """Factory for creating complete test scenarios."""

    @staticmethod
    def create_successful_conversion_scenario():
        """Create data for a successful conversion test."""
        return {
            "pptx_file": FileFactory.create_pptx_file("presentation.pptx", 500),
            "pdf_file": FileFactory.create_pdf_file("presentation.pdf", 300),
            "job_id": "successful-job-123",
            "download_url": "https://s3.amazonaws.com/test-bucket/presentation.pdf?signature=abc123",
            "filename": "presentation.pptx"
        }

    @staticmethod
    def create_conversion_failure_scenario():
        """Create data for a conversion failure test."""
        return {
            "pptx_file": FileFactory.create_pptx_file("corrupted.pptx", 100),
            "job_id": "failed-job-456",
            "error_message": "Failed to convert file: corrupted presentation",
            "filename": "corrupted.pptx"
        }

    @staticmethod
    def create_large_file_scenario():
        """Create data for a large file test."""
        return {
            "pptx_file": FileFactory.create_pptx_file("large_presentation.pptx", 5000),  # 5MB
            "pdf_file": FileFactory.create_pdf_file("large_presentation.pdf", 3000),  # 3MB
            "job_id": "large-file-job-789",
            "download_url": "https://s3.amazonaws.com/test-bucket/large_presentation.pdf?signature=def456",
            "filename": "large_presentation.pptx"
        }

    @staticmethod
    def create_concurrent_uploads_scenario(count: int = 3):
        """Create data for concurrent uploads test."""
        scenarios = []
        for i in range(count):
            scenarios.append({
                "pptx_file": FileFactory.create_pptx_file(f"presentation_{i}.pptx", 200 + i * 50),
                "pdf_file": FileFactory.create_pdf_file(f"presentation_{i}.pdf", 150 + i * 30),
                "job_id": f"concurrent-job-{i}",
                "download_url": f"https://s3.amazonaws.com/test-bucket/presentation_{i}.pdf?signature=xyz{i}",
                "filename": f"presentation_{i}.pptx"
            })
        return scenarios


class MockFactory:
    """Factory for creating mock objects."""

    @staticmethod
    def create_s3_client_mock():
        """Create a mock S3 client."""
        from unittest.mock import MagicMock
        
        mock_s3 = MagicMock()
        mock_s3.put_object.return_value = None
        mock_s3.download_file.return_value = None
        mock_s3.upload_file.return_value = None
        mock_s3.generate_presigned_url.return_value = "https://example.com/file.pdf"
        mock_s3.list_objects_v2.return_value = S3ObjectFactory.create_s3_object_list()
        mock_s3.delete_object.return_value = None
        
        return mock_s3

    @staticmethod
    def create_unoserver_response_mock(success: bool = True, pdf_content: bytes = None):
        """Create a mock Unoserver response."""
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        
        if success:
            mock_response.status_code = 200
            mock_response.content = pdf_content or FileFactory.create_pdf_file()
            mock_response.raise_for_status.return_value = None
        else:
            mock_response.status_code = 500
            mock_response.content = b"Conversion failed"
            mock_response.raise_for_status.side_effect = Exception("Conversion failed")
        
        return mock_response

    @staticmethod
    def create_celery_task_mock(job_id: str = "test-job-123"):
        """Create a mock Celery task."""
        from unittest.mock import MagicMock
        
        mock_task = MagicMock()
        mock_result = MagicMock()
        mock_result.id = job_id
        mock_task.delay.return_value = mock_result
        
        return mock_task


# Convenience functions for common test data
def get_sample_pptx() -> bytes:
    """Get a sample PPTX file for testing."""
    return FileFactory.create_pptx_file()


def get_sample_pdf() -> bytes:
    """Get a sample PDF file for testing."""
    return FileFactory.create_pdf_file()


def get_large_pptx() -> bytes:
    """Get a large PPTX file for testing."""
    return FileFactory.create_pptx_file("large.pptx", 2000)  # 2MB


def get_invalid_file() -> bytes:
    """Get an invalid file for testing."""
    return FileFactory.create_invalid_file("invalid.pptx")