"""
Unit Tests for Blob Storage Module
Using AAA (Arrange, Act, Assert) Pattern

Tests cover:
- get_blob_service_client
- slugify
- build_session_folder
- upload_bytes
- download_blob
- copy_blob_to_approved
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from azure.storage.blob import BlobServiceClient
from datetime import datetime


class TestSlugify:
    """Unit tests for the slugify function."""

    def test_slugify_simple_text(self):
        """Test slugify with simple text."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = "My Project Name"
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert result == "my-project-name"

    def test_slugify_with_special_characters(self):
        """Test slugify removes special characters."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = "Project @#$% Name!"
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert result == "project-name"

    def test_slugify_with_multiple_spaces(self):
        """Test slugify handles multiple spaces."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = "Project    Multiple   Spaces"
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert result == "project-multiple-spaces"

    def test_slugify_empty_string(self):
        """Test slugify with empty string returns 'untitled'."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = ""
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert result == "untitled"

    def test_slugify_truncates_long_text(self):
        """Test slugify truncates text longer than 80 characters."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = "a" * 100
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert len(result) == 80

    def test_slugify_with_unicode_characters(self):
        """Test slugify handles unicode characters."""
        # Arrange
        from utils.blob_storage import slugify
        input_text = "Café Résumé"
        
        # Act
        result = slugify(input_text)
        
        # Assert
        assert "caf" in result  # Should handle unicode gracefully


class TestBuildSessionFolder:
    """Unit tests for the build_session_folder function."""

    def test_build_session_folder_normal(self):
        """Test build_session_folder with normal inputs."""
        # Arrange
        from utils.blob_storage import build_session_folder
        session_title = "My Project"
        session_id = "abc12345-1234-5678-9012-abcdef123456"
        
        # Act
        result = build_session_folder(session_title, session_id)
        
        # Assert
        assert result == "my-project_abc12345"

    def test_build_session_folder_empty_title(self):
        """Test build_session_folder with empty title."""
        # Arrange
        from utils.blob_storage import build_session_folder
        session_title = ""
        session_id = "abc12345-1234-5678-9012-abcdef123456"
        
        # Act
        result = build_session_folder(session_title, session_id)
        
        # Assert
        assert result == "untitled_abc12345"

    def test_build_session_folder_short_session_id(self):
        """Test build_session_folder with short session ID."""
        # Arrange
        from utils.blob_storage import build_session_folder
        session_title = "Project"
        session_id = "abc"
        
        # Act
        result = build_session_folder(session_title, session_id)
        
        # Assert
        assert result == "project_abc"


class TestGetBlobServiceClient:
    """Unit tests for get_blob_service_client function."""

    @patch('utils.blob_storage.settings')
    @patch('utils.blob_storage.BlobServiceClient')
    def test_get_blob_service_client_returns_client(self, mock_blob_class, mock_settings):
        """Test get_blob_service_client returns a BlobServiceClient."""
        # Arrange
        from utils.blob_storage import get_blob_service_client
        mock_settings.AZURE_BLOB_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=test"
        mock_client = MagicMock()
        mock_blob_class.from_connection_string.return_value = mock_client
        
        # Act
        result = get_blob_service_client()
        
        # Assert
        assert result == mock_client
        mock_blob_class.from_connection_string.assert_called_once()


class TestUploadBytes:
    """Unit tests for upload_bytes function."""

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage._ensure_container')
    @patch('utils.blob_storage._generate_sas_url')
    @patch('utils.blob_storage.settings')
    async def test_upload_bytes_with_session_folder(
        self, mock_settings, mock_sas, mock_ensure, mock_get_client
    ):
        """Test upload_bytes with session folder."""
        # Arrange
        from utils.blob_storage import upload_bytes
        
        mock_settings.AZURE_BLOB_CONTAINER = "test-container"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_ensure.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_sas.return_value = "https://blob.url/test?sas=token"
        
        test_data = b"test file content"
        file_name = "test.pdf"
        content_type = "application/pdf"
        session_folder = "my-project_abc12345"
        
        # Act
        sas_url, storage_path = await upload_bytes(
            test_data, file_name, content_type, session_folder
        )
        
        # Assert
        assert sas_url == "https://blob.url/test?sas=token"
        assert storage_path == "my-project_abc12345/generated/test.pdf"
        mock_blob_client.upload_blob.assert_called_once()

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage._ensure_container')
    @patch('utils.blob_storage._generate_sas_url')
    @patch('utils.blob_storage.settings')
    async def test_upload_bytes_without_session_folder(
        self, mock_settings, mock_sas, mock_ensure, mock_get_client
    ):
        """Test upload_bytes without session folder uses UUID path."""
        # Arrange
        from utils.blob_storage import upload_bytes
        
        mock_settings.AZURE_BLOB_CONTAINER = "test-container"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_ensure.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_sas.return_value = "https://blob.url/test?sas=token"
        
        test_data = b"test content"
        file_name = "test.txt"
        content_type = "text/plain"
        
        # Act
        sas_url, storage_path = await upload_bytes(test_data, file_name, content_type)
        
        # Assert
        assert sas_url == "https://blob.url/test?sas=token"
        assert storage_path.startswith("generated/")
        assert storage_path.endswith("/test.txt")


class TestDownloadBlob:
    """Unit tests for download_blob function."""

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    async def test_download_blob_success(self, mock_settings, mock_get_client):
        """Test download_blob successfully downloads content."""
        # Arrange
        from utils.blob_storage import download_blob
        
        mock_settings.AZURE_BLOB_CONTAINER = "test-container"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = "https://blob.url/test"
        mock_download = MagicMock()
        mock_download.readall.return_value = b"file content"
        mock_blob_client.download_blob.return_value = mock_download
        
        storage_path = "folder/test.pdf"
        
        # Act
        result = await download_blob(storage_path)
        
        # Assert
        assert result == b"file content"

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    async def test_download_blob_with_encoded_path(self, mock_settings, mock_get_client):
        """Test download_blob handles URL-encoded paths."""
        # Arrange
        from utils.blob_storage import download_blob
        
        mock_settings.AZURE_BLOB_CONTAINER = "test-container"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = "https://blob.url/test"
        mock_download = MagicMock()
        mock_download.readall.return_value = b"content"
        mock_blob_client.download_blob.return_value = mock_download
        
        storage_path = "folder%2Ftest%20file.pdf"  # URL encoded path
        
        # Act
        result = await download_blob(storage_path)
        
        # Assert
        assert result == b"content"
        # Should decode the path
        mock_container.get_blob_client.assert_called_with("folder/test file.pdf")

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    async def test_download_blob_not_found_raises_exception(self, mock_settings, mock_get_client):
        """Test download_blob raises exception when blob not found."""
        # Arrange
        from utils.blob_storage import download_blob
        
        mock_settings.AZURE_BLOB_CONTAINER = "test-container"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        mock_blob_client.url = "https://blob.url/test"
        mock_blob_client.download_blob.side_effect = Exception("Blob not found")
        
        storage_path = "nonexistent/file.pdf"
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await download_blob(storage_path)
        assert "Blob not found" in str(exc_info.value)


class TestCopyBlobToApproved:
    """Unit tests for copy_blob_to_approved function."""

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage._ensure_container')
    @patch('utils.blob_storage._generate_sas_url')
    @patch('utils.blob_storage.settings')
    async def test_copy_blob_to_approved_success(
        self, mock_settings, mock_sas, mock_ensure, mock_get_client
    ):
        """Test copy_blob_to_approved copies blob successfully."""
        # Arrange
        from utils.blob_storage import copy_blob_to_approved
        
        mock_settings.AZURE_BLOB_CONTAINER = "artifacts"
        mock_settings.AZURE_BLOB_APPROVED_CONTAINER = "artifacts-approved"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_src_container = MagicMock()
        mock_dst_container = MagicMock()
        mock_client.get_container_client.return_value = mock_src_container
        mock_ensure.return_value = mock_dst_container
        
        mock_src_blob = MagicMock()
        mock_src_blob.url = "https://blob.url/src"
        mock_src_container.get_blob_client.return_value = mock_src_blob
        
        mock_dst_blob = MagicMock()
        mock_dst_container.get_blob_client.return_value = mock_dst_blob
        
        mock_sas.return_value = "https://blob.url/approved?sas=token"
        
        storage_path = "folder/test.pdf"
        
        # Act
        sas_url, new_path = await copy_blob_to_approved(storage_path)
        
        # Assert
        assert sas_url == "https://blob.url/approved?sas=token"
        assert new_path == storage_path
        mock_dst_blob.start_copy_from_url.assert_called_once_with("https://blob.url/src")


class TestListApprovedArtifacts:
    """Unit tests for list_approved_artifacts function."""

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    def test_list_approved_artifacts_returns_expected_shape(self, mock_settings, mock_get_client):
        # Arrange
        from utils.blob_storage import list_approved_artifacts
        mock_settings.AZURE_BLOB_APPROVED_CONTAINER = "artifacts-approved"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        # Simulate two blobs
        mock_blob1 = MagicMock()
        mock_blob1.name = "file1.pdf"
        mock_blob1.size = 1234
        mock_blob1.last_modified = datetime(2024, 1, 1)
        mock_blob1.metadata = {"approved_by": "Admin", "created_by": "User1"}
        mock_blob2 = MagicMock()
        mock_blob2.name = "file2.xlsx"
        mock_blob2.size = 5678
        mock_blob2.last_modified = datetime(2024, 2, 2)
        mock_blob2.metadata = {}
        mock_container.list_blobs.return_value = [mock_blob1, mock_blob2]
        # get_blob_properties returns content_settings
        mock_blob_client.get_blob_properties.side_effect = [
            MagicMock(content_settings=MagicMock(content_type="application/pdf")),
            MagicMock(content_settings=MagicMock(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
        ]
        # _generate_sas_url returns a dummy URL
        with patch('utils.blob_storage._generate_sas_url', side_effect=lambda *a, **kw: f"https://blob/{a[2]}"):
            # Act
            import asyncio
            result = asyncio.run(list_approved_artifacts())
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "file1.pdf"
        assert result[0]["approved_by"] == "Admin"
        assert result[0]["created_by"] == "User1"
        assert result[0]["content_type"] == "application/pdf"
        assert result[1]["name"] == "file2.xlsx"
        assert result[1]["approved_by"] is None
        assert result[1]["created_by"] is None
        assert result[1]["content_type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class TestGetApprovedArtifactUrl:
    """Unit tests for get_approved_artifact_url function."""

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    def test_get_approved_artifact_url_success(self, mock_settings, mock_get_client):
        # Arrange
        from utils.blob_storage import get_approved_artifact_url
        mock_settings.AZURE_BLOB_APPROVED_CONTAINER = "artifacts-approved"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        # get_blob_properties does not raise
        mock_blob_client.get_blob_properties.return_value = MagicMock()
        # _generate_sas_url returns a dummy URL
        with patch('utils.blob_storage._generate_sas_url', return_value="https://blob/file1.pdf"):
            import asyncio
            result = asyncio.run(get_approved_artifact_url("file1.pdf"))
        assert result == "https://blob/file1.pdf"

    @pytest.mark.asyncio
    @patch('utils.blob_storage.get_blob_service_client')
    @patch('utils.blob_storage.settings')
    def test_get_approved_artifact_url_not_found(self, mock_settings, mock_get_client):
        # Arrange
        from utils.blob_storage import get_approved_artifact_url
        mock_settings.AZURE_BLOB_APPROVED_CONTAINER = "artifacts-approved"
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        mock_blob_client = MagicMock()
        mock_container.get_blob_client.return_value = mock_blob_client
        # get_blob_properties raises ResourceNotFoundError
        from azure.core.exceptions import ResourceNotFoundError
        mock_blob_client.get_blob_properties.side_effect = ResourceNotFoundError("not found")
        import asyncio
        with pytest.raises(FileNotFoundError):
            asyncio.run(get_approved_artifact_url("missing.pdf"))
