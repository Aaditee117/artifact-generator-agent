"""
Unit Tests for Architecture Tool Module
Using AAA (Arrange, Act, Assert) Pattern

Tests cover:
- generate_architecture_diagram
- _normalize_graph
- Graph structure validation
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json


class TestGenerateArchitectureDiagram:
    """Unit tests for generate_architecture_diagram function."""

    @pytest.mark.asyncio
    @patch('tools.architecture_tool._get_chat_client')
    async def test_generate_architecture_diagram_poc(self, mock_client):
        """Test generating POC architecture diagram."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "project_name": "Test Project",
            "architecture_style": "microservices",
            "groups": [
                {"id": "frontend", "label": "Frontend Tier", "position": {"x": 0, "y": 0}}
            ],
            "nodes": [
                {"id": "webapp", "label": "Web App", "type": "service", "groupId": "frontend"}
            ],
            "edges": []
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        context = "Simple web application"
        instructions = "Create basic architecture"
        
        # Act
        result = await generate_architecture_diagram(context, instructions, phase_type="poc")
        
        # Assert
        assert result["project_name"] == "Test Project"
        assert result["architecture_style"] == "microservices"
        assert result["phase_type"] == "poc"
        assert "graph" in result

    @pytest.mark.asyncio
    @patch('tools.architecture_tool._get_chat_client')
    async def test_generate_architecture_diagram_mvp(self, mock_client):
        """Test generating MVP architecture diagram."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "project_name": "Production App",
            "architecture_style": "hybrid",
            "groups": [
                {"id": "frontend", "label": "Frontend", "position": {"x": 0, "y": 0}},
                {"id": "backend", "label": "Backend", "position": {"x": 200, "y": 0}},
                {"id": "data", "label": "Data Tier", "position": {"x": 400, "y": 0}}
            ],
            "nodes": [
                {"id": "cdn", "label": "Azure CDN", "type": "service", "groupId": "frontend"},
                {"id": "api", "label": "API Management", "type": "service", "groupId": "backend"},
                {"id": "sql", "label": "Azure SQL", "type": "database", "groupId": "data"}
            ],
            "edges": [
                {"source": "cdn", "target": "api"},
                {"source": "api", "target": "sql"}
            ]
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        context = "Enterprise application with high availability"
        instructions = "Create production-ready architecture"
        
        # Act
        result = await generate_architecture_diagram(context, instructions, phase_type="mvp")
        
        # Assert
        assert result["project_name"] == "Production App"
        assert result["phase_type"] == "mvp"
        assert result["phase_label"] == "MVP"
        assert len(result["graph"]["groups"]) == 3
        assert len(result["graph"]["nodes"]) == 3
        assert len(result["graph"]["edges"]) == 2

    @pytest.mark.asyncio
    @patch('tools.architecture_tool._get_chat_client')
    async def test_generate_architecture_diagram_default_phase(self, mock_client):
        """Test generating architecture without specific phase."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "project_name": "Generic Project",
            "architecture_style": "monolithic",
            "groups": [],
            "nodes": [{"id": "app", "label": "Application", "type": "service"}],
            "edges": []
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        # Act
        result = await generate_architecture_diagram("context", "instructions")
        
        # Assert
        assert result["phase_type"] is None
        assert result["phase_label"] is None


class TestNormalizeGraph:
    """Unit tests for _normalize_graph function."""

    def test_normalize_graph_with_valid_input(self):
        """Test normalizing valid graph structure."""
        # Arrange
        from tools.architecture_tool import _normalize_graph
        
        spec = {
            "groups": [{"id": "g1", "label": "Group 1"}],
            "nodes": [{"id": "n1", "label": "Node 1", "groupId": "g1"}],
            "edges": [{"source": "n1", "target": "n1"}]
        }
        
        # Act
        result = _normalize_graph(spec)
        
        # Assert
        assert "groups" in result
        assert "nodes" in result
        assert "edges" in result
        assert len(result["groups"]) == 1
        assert len(result["nodes"]) == 1

    def test_normalize_graph_with_empty_input(self):
        """Test normalizing empty graph."""
        # Arrange
        from tools.architecture_tool import _normalize_graph
        
        spec = {}
        
        # Act
        result = _normalize_graph(spec)
        
        # Assert
        assert result["groups"] == []
        assert result["nodes"] == []
        assert result["edges"] == []

    def test_normalize_graph_with_missing_fields(self):
        """Test normalizing graph with missing fields."""
        # Arrange
        from tools.architecture_tool import _normalize_graph
        
        spec = {
            "nodes": [{"id": "n1", "label": "Node 1"}]
            # Missing groups and edges
        }
        
        # Act
        result = _normalize_graph(spec)
        
        # Assert
        assert result["groups"] == []
        assert len(result["nodes"]) == 1
        assert result["edges"] == []


class TestGetChatClient:
    """Unit tests for _get_chat_client function."""

    @patch('tools.architecture_tool.settings')
    @patch('tools.architecture_tool.AzureOpenAI')
    def test_get_chat_client_returns_azure_openai(self, mock_azure, mock_settings):
        """Test _get_chat_client returns AzureOpenAI instance."""
        # Arrange
        from tools.architecture_tool import _get_chat_client
        
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_API_VERSION = "2024-02-01"
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_client = MagicMock()
        mock_azure.return_value = mock_client
        
        # Act
        result = _get_chat_client()
        
        # Assert
        assert result == mock_client
        mock_azure.assert_called_once_with(
            api_key="test-key",
            api_version="2024-02-01",
            azure_endpoint="https://test.openai.azure.com"
        )
