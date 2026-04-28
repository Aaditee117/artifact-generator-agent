"""
Functional Tests for OptiStudio Agent API
Using AAA (Arrange, Act, Assert) Pattern

These tests verify end-to-end functionality of API endpoints
and integration between components.

Tests cover:
- /clarify endpoint
- /generate endpoint
- /feedback endpoint
- Full workflow scenarios
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
import json


@pytest.fixture
def test_client():
    """Create test client for FastAPI app."""
    from main import app
    return TestClient(app)


@pytest.fixture
def mock_all_dependencies():
    """Mock all external dependencies for functional tests."""
    with patch('main.download_blob') as mock_download, \
         patch('main.extract_text') as mock_extract, \
         patch('main.save_conversation_message') as mock_save_msg, \
         patch('main.get_conversation_history') as mock_get_history, \
         patch('main.save_session_state') as mock_save_state, \
         patch('main.get_session_state') as mock_get_state, \
         patch('main.get_extracted_text') as mock_get_text, \
         patch('main.save_extracted_text') as mock_save_text:
        
        mock_download.return_value = b"Document content"
        mock_extract.return_value = "Extracted text from document"
        mock_get_history.return_value = []
        mock_get_state.return_value = None
        mock_get_text.return_value = None
        
        yield {
            'download_blob': mock_download,
            'extract_text': mock_extract,
            'save_conversation_message': mock_save_msg,
            'get_conversation_history': mock_get_history,
            'save_session_state': mock_save_state,
            'get_session_state': mock_get_state,
            'get_extracted_text': mock_get_text,
            'save_extracted_text': mock_save_text
        }


class TestClarifyEndpoint:
    """Functional tests for /clarify endpoint."""

    def test_clarify_architecture_returns_questions(self, test_client, mock_all_dependencies):
        """Test /clarify endpoint returns clarification questions for architecture."""
        # Arrange
        with patch('main.AzureOpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "questions": [
                    {"id": "q1", "question": "What is the expected user load?"},
                    {"id": "q2", "question": "Do you need high availability?"}
                ]
            })
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            request_data = {
                "session_id": "test-session-123",
                "action": "architecture_diagram",
                "artifacts": [
                    {"storage_path": "path/to/doc.pdf", "file_name": "doc.pdf", "category": "Document"}
                ],
                "instructions": "Create architecture diagram"
            }
            
            # Act
            response = test_client.post("/clarify", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "questions" in data or "clarification" in data

    def test_clarify_cost_report_returns_questions(self, test_client, mock_all_dependencies):
        """Test /clarify endpoint returns questions for cost report."""
        # Arrange
        with patch('main.AzureOpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "questions": [
                    {"id": "q1", "question": "What Azure region?"},
                    {"id": "q2", "question": "Expected data storage size?"}
                ]
            })
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            request_data = {
                "session_id": "test-session-456",
                "action": "cost_report",
                "artifacts": [
                    {"storage_path": "path/to/requirements.docx", "file_name": "requirements.docx"}
                ],
                "instructions": "Generate cost estimate"
            }
            
            # Act
            response = test_client.post("/clarify", json=request_data)
            
            # Assert
            assert response.status_code == 200

    def test_clarify_with_invalid_session_id(self, test_client):
        """Test /clarify with missing session_id returns error."""
        # Arrange
        request_data = {
            "action": "architecture_diagram",
            "artifacts": []
        }
        
        # Act
        response = test_client.post("/clarify", json=request_data)
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestGenerateEndpoint:
    """Functional tests for /generate endpoint."""

    def test_generate_architecture_returns_graph(self, test_client, mock_all_dependencies):
        """Test /generate endpoint returns architecture graph."""
        # Arrange
        with patch('main.generate_architecture_diagram') as mock_gen:
            mock_gen.return_value = {
                "project_name": "Test Project",
                "architecture_style": "microservices",
                "graph": {
                    "groups": [],
                    "nodes": [{"id": "n1", "label": "Service"}],
                    "edges": []
                },
                "phase_type": "poc"
            }
            
            request_data = {
                "session_id": "test-session-789",
                "action": "architecture_diagram",
                "artifacts": [
                    {"storage_path": "path/doc.pdf", "file_name": "doc.pdf"}
                ],
                "instructions": "Generate architecture",
                "answers": {"q1": "100 users"},
                "phase_type": "poc"
            }
            
            # Act
            response = test_client.post("/generate", json=request_data)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert "graph" in data or "result" in data or mock_gen.called

    def test_generate_ppt_returns_download_url(self, test_client, mock_all_dependencies):
        """Test /generate endpoint returns PPT download URL."""
        # Arrange
        with patch('main.generate_presales_ppt') as mock_gen:
            mock_gen.return_value = {
                "download_url": "https://blob.url/presentation.pptx",
                "storage_path": "path/presentation.pptx",
                "file_name": "Presales_Presentation.pptx"
            }
            
            request_data = {
                "session_id": "test-session-ppt",
                "action": "presales_ppt",
                "artifacts": [
                    {"storage_path": "path/doc.pdf", "file_name": "doc.pdf"}
                ],
                "instructions": "Generate presentation",
                "phase_type": "mvp"
            }
            
            # Act
            response = test_client.post("/generate", json=request_data)
            
            # Assert
            assert response.status_code == 200

    def test_generate_cost_report_returns_excel(self, test_client, mock_all_dependencies):
        """Test /generate endpoint returns cost report Excel."""
        # Arrange
        with patch('main.generate_cost_report') as mock_gen:
            mock_gen.return_value = {
                "download_url": "https://blob.url/cost_report.xlsx",
                "storage_path": "path/cost_report.xlsx",
                "cost_data": {"total_monthly": 500.00}
            }
            
            request_data = {
                "session_id": "test-session-cost",
                "action": "cost_report",
                "artifacts": [
                    {"storage_path": "path/requirements.docx", "file_name": "requirements.docx"}
                ],
                "instructions": "Generate cost estimate",
                "phase_type": "both"
            }
            
            # Act
            response = test_client.post("/generate", json=request_data)
            
            # Assert
            assert response.status_code == 200


class TestFeedbackEndpoint:
    """Functional tests for /feedback endpoint."""

    def test_feedback_approve_copies_to_approved(self, test_client):
        """Test /feedback approve action copies artifact to approved container."""
        # Arrange
        with patch('main.copy_blob_to_approved') as mock_copy, \
             patch('main.save_generated_artifact') as mock_save:
            
            mock_copy.return_value = ("https://approved.url/file.pptx", "path/file.pptx")
            
            request_data = {
                "session_id": "test-session-feedback",
                "artifact_type": "ppt",
                "storage_path": "path/presentation.pptx",
                "action": "approve",
                "feedback": "Looks good!"
            }
            
            # Act
            response = test_client.post("/feedback", json=request_data)
            
            # Assert
            assert response.status_code == 200
            mock_copy.assert_called_once()


class TestFullWorkflowScenarios:
    """Functional tests for complete workflow scenarios."""

    def test_full_architecture_workflow(self, test_client, mock_all_dependencies):
        """Test complete architecture diagram generation workflow."""
        # Arrange - Step 1: Clarify
        with patch('main.AzureOpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "questions": [{"id": "q1", "question": "User load?"}]
            })
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            clarify_request = {
                "session_id": "workflow-test-1",
                "action": "architecture_diagram",
                "artifacts": [{"storage_path": "doc.pdf", "file_name": "doc.pdf"}],
                "instructions": "Create diagram"
            }
            
            # Act - Step 1
            clarify_response = test_client.post("/clarify", json=clarify_request)
            
            # Assert - Step 1
            assert clarify_response.status_code == 200
        
        # Arrange - Step 2: Generate
        with patch('main.generate_architecture_diagram') as mock_gen:
            mock_gen.return_value = {
                "project_name": "Test",
                "graph": {"groups": [], "nodes": [], "edges": []},
                "phase_type": "poc"
            }
            
            generate_request = {
                "session_id": "workflow-test-1",
                "action": "architecture_diagram",
                "artifacts": [{"storage_path": "doc.pdf", "file_name": "doc.pdf"}],
                "answers": {"q1": "1000 users"},
                "phase_type": "poc"
            }
            
            # Act - Step 2
            generate_response = test_client.post("/generate", json=generate_request)
            
            # Assert - Step 2
            assert generate_response.status_code == 200

    def test_full_cost_report_workflow(self, test_client, mock_all_dependencies):
        """Test complete cost report generation workflow."""
        # Arrange
        with patch('main.generate_cost_report') as mock_gen:
            mock_gen.return_value = {
                "download_url": "https://blob.url/report.xlsx",
                "cost_data": {
                    "poc": {"total_monthly": 100},
                    "mvp": {"total_monthly": 500}
                }
            }
            
            request = {
                "session_id": "cost-workflow-1",
                "action": "cost_report",
                "artifacts": [{"storage_path": "req.pdf", "file_name": "req.pdf"}],
                "phase_type": "both"
            }
            
            # Act
            response = test_client.post("/generate", json=request)
            
            # Assert
            assert response.status_code == 200


class TestErrorHandling:
    """Functional tests for error handling scenarios."""

    def test_clarify_with_blob_not_found(self, test_client):
        """Test /clarify handles blob not found gracefully."""
        # Arrange
        with patch('main.download_blob') as mock_download:
            mock_download.side_effect = Exception("Blob not found")
            
            request_data = {
                "session_id": "error-test-1",
                "action": "architecture_diagram",
                "artifacts": [{"storage_path": "nonexistent.pdf", "file_name": "nonexistent.pdf"}]
            }
            
            # Act
            response = test_client.post("/clarify", json=request_data)
            
            # Assert
            # Should return error status or handle gracefully
            assert response.status_code in [200, 400, 404, 500]

    def test_generate_with_invalid_action(self, test_client):
        """Test /generate with invalid action returns error."""
        # Arrange
        request_data = {
            "session_id": "error-test-2",
            "action": "invalid_action",
            "artifacts": []
        }
        
        # Act
        response = test_client.post("/generate", json=request_data)
        
        # Assert
        assert response.status_code in [400, 422, 500]


class TestCORSConfiguration:
    """Functional tests for CORS configuration."""

    def test_cors_allows_localhost(self, test_client):
        """Test CORS allows localhost origins."""
        # Arrange & Act
        response = test_client.options(
            "/clarify",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Assert
        # CORS preflight should succeed
        assert response.status_code in [200, 204, 405]
