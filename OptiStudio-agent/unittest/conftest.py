"""
Pytest fixtures and configuration for OptiStudio Agent tests.

This module provides comprehensive fixtures for:
- Unit tests (mocked dependencies)
- Functional tests (API testing)
- Integration tests (component interaction)

All tests follow the AAA (Arrange, Act, Assert) pattern.
"""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "functional: mark test as a functional test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# ============================================================================
# Azure OpenAI Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock Azure OpenAI client."""
    client = MagicMock()
    client.chat.completions.create = MagicMock()
    return client


@pytest.fixture
def mock_openai_response():
    """Mock a successful OpenAI API response."""
    def _create_response(content: dict | str):
        response = MagicMock()
        response.choices = [MagicMock()]
        if isinstance(content, dict):
            response.choices[0].message.content = json.dumps(content)
        else:
            response.choices[0].message.content = content
        return response
    return _create_response


@pytest.fixture
def mock_azure_openai():
    """Mock AzureOpenAI class with configurable responses."""
    with patch('openai.AzureOpenAI') as mock_class:
        mock_client = MagicMock()
        mock_class.return_value = mock_client
        yield mock_client


# ============================================================================
# Azure Blob Storage Fixtures
# ============================================================================

@pytest.fixture
def mock_blob_storage():
    """Mock Azure Blob Storage."""
    storage = AsyncMock()
    storage.upload_bytes = AsyncMock(return_value=("https://blob.url/file.pdf", "path/to/file.pdf"))
    return storage


@pytest.fixture
def mock_blob_service_client():
    """Mock BlobServiceClient with full functionality."""
    with patch('utils.blob_storage.BlobServiceClient') as mock_class:
        mock_client = MagicMock()
        mock_client.account_name = "testaccount"
        mock_client.credential.account_key = "testkey"
        
        mock_container = MagicMock()
        mock_client.get_container_client.return_value = mock_container
        
        mock_blob = MagicMock()
        mock_blob.url = "https://testaccount.blob.core.windows.net/test"
        mock_container.get_blob_client.return_value = mock_blob
        
        mock_class.from_connection_string.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_blob_download():
    """Mock blob download with configurable content."""
    def _create_download(content: bytes):
        mock_download = MagicMock()
        mock_download.readall.return_value = content
        return mock_download
    return _create_download


# ============================================================================
# Cosmos DB Fixtures
# ============================================================================

@pytest.fixture
def mock_cosmos_service():
    """Mock Cosmos DB service functions."""
    with patch('utils.cosmos_service.save_extracted_text') as mock_save_text, \
         patch('utils.cosmos_service.get_extracted_text') as mock_get_text, \
         patch('utils.cosmos_service.save_conversation_message') as mock_save_msg, \
         patch('utils.cosmos_service.get_conversation_history') as mock_get_history, \
         patch('utils.cosmos_service.save_session_state') as mock_save_state, \
         patch('utils.cosmos_service.get_session_state') as mock_get_state:
        
        mock_get_text.return_value = None
        mock_get_history.return_value = []
        mock_get_state.return_value = None
        
        yield {
            'save_extracted_text': mock_save_text,
            'get_extracted_text': mock_get_text,
            'save_conversation_message': mock_save_msg,
            'get_conversation_history': mock_get_history,
            'save_session_state': mock_save_state,
            'get_session_state': mock_get_state
        }


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_project_context():
    """Sample project context for testing."""
    return """
    Project: AI Document Processing System
    Client: Acme Corp
    Description: Build an AI-powered document processing system that can:
    - Extract text from PDFs and images
    - Classify documents
    - Generate summaries
    Technologies: Azure OpenAI, Azure AI Search, Python, React
    Timeline: 3 months
    """


@pytest.fixture
def sample_architecture_response():
    """Sample architecture diagram response."""
    return {
        "project_name": "AI Document Processing",
        "architecture_style": "microservices",
        "groups": [
            {"id": "frontend", "label": "Frontend Tier", "position": {"x": 0, "y": 0}},
            {"id": "backend", "label": "Backend Services", "position": {"x": 200, "y": 0}},
            {"id": "data", "label": "Data Layer", "position": {"x": 400, "y": 0}}
        ],
        "nodes": [
            {"id": "webapp", "label": "React Web App", "type": "webapp", "groupId": "frontend"},
            {"id": "api", "label": "FastAPI Backend", "type": "api", "groupId": "backend"},
            {"id": "cosmos", "label": "Cosmos DB", "type": "database", "groupId": "data"}
        ],
        "edges": [
            {"source": "webapp", "target": "api"},
            {"source": "api", "target": "cosmos"}
        ]
    }


@pytest.fixture
def sample_cost_report_data():
    """Sample cost report data."""
    return {
        "report_title": "Azure Cost Estimate",
        "client": "Acme Corp",
        "generated_date": datetime.now().isoformat(),
        "poc": {
            "phase_name": "Proof of Concept",
            "services": [
                {
                    "service_category": "Compute",
                    "service_type": "Azure App Service",
                    "custom_name": "Web Application",
                    "region": "East US",
                    "description": "Basic B1 tier for POC",
                    "monthly_cost": 54.75,
                    "upfront_cost": 0.00
                },
                {
                    "service_category": "Database",
                    "service_type": "Azure Cosmos DB",
                    "custom_name": "Document Store",
                    "region": "East US",
                    "description": "Serverless tier",
                    "monthly_cost": 25.00,
                    "upfront_cost": 0.00
                }
            ],
            "total_monthly": 79.75,
            "total_upfront": 0.00
        },
        "mvp": {
            "phase_name": "Minimum Viable Product",
            "services": [
                {
                    "service_category": "Compute",
                    "service_type": "Azure App Service",
                    "custom_name": "Web Application",
                    "region": "East US",
                    "description": "Standard S2 tier for production",
                    "monthly_cost": 146.00,
                    "upfront_cost": 0.00
                },
                {
                    "service_category": "Database",
                    "service_type": "Azure Cosmos DB",
                    "custom_name": "Document Store",
                    "region": "East US",
                    "description": "Provisioned throughput",
                    "monthly_cost": 150.00,
                    "upfront_cost": 0.00
                },
                {
                    "service_category": "AI + Machine Learning",
                    "service_type": "Azure OpenAI Service",
                    "custom_name": "GPT-4 API",
                    "region": "East US",
                    "description": "Pay-as-you-go",
                    "monthly_cost": 200.00,
                    "upfront_cost": 0.00
                }
            ],
            "total_monthly": 496.00,
            "total_upfront": 0.00
        }
    }


@pytest.fixture
def sample_ppt_content():
    """Sample PPT content for testing."""
    return {
        "title_slide": {
            "title": "AI Document Processing — MVP Proposal",
            "client": "Acme Corp",
            "date": "April 2026"
        },
        "our_understanding": {
            "sections": [
                {
                    "header": "Our Understanding",
                    "points": ["Client needs automated document processing", "Current manual process is slow"]
                },
                {
                    "header": "Current Challenges",
                    "points": ["High volume of documents", "Manual errors in classification"]
                },
                {
                    "header": "AI Opportunity",
                    "points": ["AI can automate extraction and classification", "Reduce processing time by 80%"]
                }
            ]
        },
        "objective": {
            "points": [
                "Automate document extraction with 95% accuracy",
                "Implement intelligent document classification",
                "Reduce manual processing time by 80%"
            ]
        },
        "scope": {
            "points": [
                "PDF and image text extraction",
                "Document classification engine",
                "Summary generation",
                "User dashboard"
            ]
        },
        "high_level_design": {
            "note": "Architecture diagram will be auto-inserted"
        },
        "prerequisites": {
            "items": [
                {"category": "Azure Environment Access", "description": "Contributor access to Azure subscription"},
                {"category": "Source Documents", "description": "Sample documents for training"},
                {"category": "DevOps Setup", "description": "GitHub repo and pipeline configured"}
            ]
        },
        "definition_of_done": {
            "items": [
                {"section": "Development Completion", "description": "All features implemented and tested"},
                {"section": "Documentation & Stakeholder Sign-off", "description": "Architecture docs delivered"},
                {"section": "Production Readiness", "description": "Monitoring and security validated"}
            ]
        },
        "out_of_scope": {
            "points": ["Mobile application", "Multi-language support", "Real-time processing"]
        },
        "timeline_cost": {
            "phases": [
                {"phase": "Phase 1: Discovery", "duration": "2 weeks"},
                {"phase": "Phase 2: Development", "duration": "8 weeks"},
                {"phase": "Phase 3: Testing", "duration": "2 weeks"}
            ]
        },
        "cost_estimate": {
            "items": [
                {"service": "Development Team", "cost": "Based on timeline"},
                {"service": "Azure Infrastructure (Monthly)", "cost": "~$500/mo"}
            ]
        },
        "next_steps": {
            "steps": ["Contract finalization", "Kickoff meeting", "Sprint planning", "Development start"]
        }
    }
