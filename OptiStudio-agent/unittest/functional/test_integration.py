"""
Functional Tests for Component Integration
Using AAA (Arrange, Act, Assert) Pattern

These tests verify integration between different components
of the OptiStudio Agent system.

Tests cover:
- Document processing pipeline
- Artifact generation pipeline
- Cost report generation pipeline
- PPT generation pipeline
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json


class TestDocumentProcessingPipeline:
    """Functional tests for document processing integration."""

    @pytest.mark.asyncio
    async def test_blob_to_text_extraction_pipeline(self):
        """Test complete pipeline from blob download to text extraction."""
        # Arrange
        from utils.blob_storage import download_blob
        from utils.document_reader import extract_text
        
        with patch('utils.blob_storage.get_blob_service_client') as mock_client, \
             patch('utils.blob_storage.settings') as mock_settings:
            
            mock_settings.AZURE_BLOB_CONTAINER = "test"
            mock_container = MagicMock()
            mock_client.return_value.get_container_client.return_value = mock_container
            mock_blob = MagicMock()
            mock_blob.url = "https://blob.url"
            mock_container.get_blob_client.return_value = mock_blob
            
            # Simulate a text file
            mock_download = MagicMock()
            mock_download.readall.return_value = b"Project Requirements:\n1. Build web app\n2. Deploy to Azure"
            mock_blob.download_blob.return_value = mock_download
            
            # Act
            blob_data = await download_blob("path/requirements.txt")
            text = await extract_text(blob_data, "requirements.txt")
            
            # Assert
            assert "Project Requirements" in text
            assert "Build web app" in text
            assert "Deploy to Azure" in text

    @pytest.mark.asyncio
    async def test_multiple_document_aggregation(self):
        """Test processing and aggregating multiple documents."""
        # Arrange
        from utils.document_reader import extract_text
        
        documents = [
            (b"Document 1: Architecture Overview", "arch.txt"),
            (b"Document 2: Business Requirements", "requirements.txt"),
            (b"Document 3: Technical Specifications", "specs.txt")
        ]
        
        # Act
        extracted_texts = []
        for data, name in documents:
            text = await extract_text(data, name)
            extracted_texts.append(text)
        
        combined_context = "\n\n".join(extracted_texts)
        
        # Assert
        assert "Architecture Overview" in combined_context
        assert "Business Requirements" in combined_context
        assert "Technical Specifications" in combined_context
        assert len(extracted_texts) == 3


class TestCostReportGenerationPipeline:
    """Functional tests for cost report generation integration."""

    @pytest.mark.asyncio
    async def test_cost_report_excel_generation(self):
        """Test cost data to Excel generation pipeline."""
        # Arrange
        from utils.cost_report_generator import generate_cost_excel
        
        cost_data = {
            "report_title": "Azure Cost Estimate",
            "client": "Test Client",
            "generated_date": "2026-04-16",
            "poc": {
                "phase_name": "POC",
                "services": [
                    {
                        "service_category": "Compute",
                        "service_type": "App Service",
                        "custom_name": "Web App",
                        "region": "East US",
                        "description": "Basic tier for POC",
                        "monthly_cost": 50.00,
                        "upfront_cost": 0.00
                    }
                ],
                "total_monthly": 50.00,
                "total_upfront": 0.00
            }
        }
        
        # Act
        excel_bytes = generate_cost_excel(cost_data)
        
        # Assert
        assert excel_bytes is not None
        assert len(excel_bytes) > 0
        # Excel files start with PK (zip format)
        assert excel_bytes[:2] == b'PK'

    @pytest.mark.asyncio
    async def test_cost_report_poc_mvp_comparison(self):
        """Test POC vs MVP cost comparison report generation."""
        # Arrange
        from utils.cost_report_generator import generate_cost_excel
        
        cost_data = {
            "report_title": "Azure Cost Comparison",
            "client": "Acme Corp",
            "poc": {
                "phase_name": "Proof of Concept",
                "services": [
                    {"service_category": "Compute", "service_type": "App Service", 
                     "monthly_cost": 50.00, "upfront_cost": 0.00}
                ],
                "total_monthly": 50.00
            },
            "mvp": {
                "phase_name": "Minimum Viable Product",
                "services": [
                    {"service_category": "Compute", "service_type": "App Service Premium",
                     "monthly_cost": 200.00, "upfront_cost": 0.00},
                    {"service_category": "Database", "service_type": "Azure SQL",
                     "monthly_cost": 150.00, "upfront_cost": 0.00}
                ],
                "total_monthly": 350.00
            }
        }
        
        # Act
        excel_bytes = generate_cost_excel(cost_data)
        
        # Assert
        assert excel_bytes is not None
        assert len(excel_bytes) > 100  # Should be a valid Excel file


class TestArchitectureGenerationPipeline:
    """Functional tests for architecture diagram generation integration."""

    @pytest.mark.asyncio
    async def test_context_to_architecture_graph(self):
        """Test context processing to architecture graph generation."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        with patch('tools.architecture_tool._get_chat_client') as mock_client:
            mock_openai = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "project_name": "E-Commerce Platform",
                "architecture_style": "microservices",
                "groups": [
                    {"id": "frontend", "label": "Frontend Tier", "position": {"x": 0, "y": 0}},
                    {"id": "backend", "label": "Backend Services", "position": {"x": 200, "y": 0}},
                    {"id": "data", "label": "Data Layer", "position": {"x": 400, "y": 0}}
                ],
                "nodes": [
                    {"id": "spa", "label": "React SPA", "type": "webapp", "groupId": "frontend"},
                    {"id": "api", "label": "API Gateway", "type": "gateway", "groupId": "backend"},
                    {"id": "orders", "label": "Order Service", "type": "service", "groupId": "backend"},
                    {"id": "sql", "label": "Azure SQL", "type": "database", "groupId": "data"}
                ],
                "edges": [
                    {"source": "spa", "target": "api"},
                    {"source": "api", "target": "orders"},
                    {"source": "orders", "target": "sql"}
                ]
            })
            mock_openai.chat.completions.create.return_value = mock_response
            mock_client.return_value = mock_openai
            
            context = """
            E-Commerce Platform Requirements:
            - React frontend for customers
            - Microservices backend
            - Order management system
            - SQL database for transactions
            """
            
            # Act
            result = await generate_architecture_diagram(
                context=context,
                instructions="Create microservices architecture",
                phase_type="mvp"
            )
            
            # Assert
            assert result["project_name"] == "E-Commerce Platform"
            assert result["architecture_style"] == "microservices"
            assert len(result["graph"]["groups"]) == 3
            assert len(result["graph"]["nodes"]) == 4
            assert len(result["graph"]["edges"]) == 3


class TestPPTGenerationPipeline:
    """Functional tests for PowerPoint generation integration."""

    @pytest.mark.asyncio
    async def test_ppt_content_generation(self):
        """Test PPT content structure generation."""
        # Arrange
        from tools.ppt_tool import generate_presales_ppt
        
        with patch('tools.ppt_tool._get_chat_client') as mock_client, \
             patch('tools.ppt_tool.fill_pptx_template') as mock_fill, \
             patch('tools.ppt_tool.upload_bytes') as mock_upload:
            
            mock_openai = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "title_slide": {"title": "Project Proposal", "client": "Acme"},
                "our_understanding": {"sections": []},
                "objective": {"points": ["Implement solution"]},
                "scope": {"points": ["Frontend", "Backend"]},
                "prerequisites": {"items": []},
                "definition_of_done": {"items": []},
                "out_of_scope": {"points": []},
                "timeline_cost": {"phases": []}
            })
            mock_openai.chat.completions.create.return_value = mock_response
            mock_client.return_value = mock_openai
            
            mock_fill.return_value = b"pptx file bytes"
            mock_upload.return_value = ("https://blob.url/ppt.pptx", "path/ppt.pptx")
            
            context = "Build a web application"
            
            # Act
            result = await generate_presales_ppt(
                context=context,
                instructions="Create proposal",
                phase_type="poc"
            )
            
            # Assert
            assert "download_url" in result or mock_upload.called


class TestSessionWorkflowIntegration:
    """Functional tests for session-based workflow integration."""

    @pytest.mark.asyncio
    async def test_session_folder_creation_and_artifact_upload(self):
        """Test session folder creation and artifact upload."""
        # Arrange
        from utils.blob_storage import build_session_folder, upload_bytes
        
        with patch('utils.blob_storage.get_blob_service_client') as mock_client, \
             patch('utils.blob_storage._ensure_container') as mock_ensure, \
             patch('utils.blob_storage._generate_sas_url') as mock_sas, \
             patch('utils.blob_storage.settings') as mock_settings:
            
            mock_settings.AZURE_BLOB_CONTAINER = "artifacts"
            mock_container = MagicMock()
            mock_ensure.return_value = mock_container
            mock_blob = MagicMock()
            mock_container.get_blob_client.return_value = mock_blob
            mock_sas.return_value = "https://blob.url/file?sas=token"
            
            session_title = "AI Document Processing Project"
            session_id = "abc12345-6789-0123-4567-89abcdef0123"
            
            # Act
            folder = build_session_folder(session_title, session_id)
            sas_url, storage_path = await upload_bytes(
                data=b"Generated content",
                file_name="output.pdf",
                content_type="application/pdf",
                session_folder=folder
            )
            
            # Assert
            assert folder == "ai-document-processing-project_abc12345"
            assert storage_path == "ai-document-processing-project_abc12345/generated/output.pdf"
            assert "sas=token" in sas_url


class TestPhaseBasedGeneration:
    """Functional tests for phase-based artifact generation."""

    @pytest.mark.asyncio
    async def test_poc_generates_minimal_architecture(self):
        """Test POC phase generates minimal architecture."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        with patch('tools.architecture_tool._get_chat_client') as mock_client:
            mock_openai = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "project_name": "POC Project",
                "architecture_style": "simple",
                "groups": [{"id": "app", "label": "Application"}],
                "nodes": [
                    {"id": "webapp", "label": "Web App (Basic)", "groupId": "app"}
                ],
                "edges": []
            })
            mock_openai.chat.completions.create.return_value = mock_response
            mock_client.return_value = mock_openai
            
            # Act
            result = await generate_architecture_diagram(
                context="Simple app",
                instructions="Create minimal architecture",
                phase_type="poc"
            )
            
            # Assert
            assert result["phase_type"] == "poc"
            assert result["phase_label"] == "POC"
            assert len(result["graph"]["nodes"]) <= 5  # POC should be minimal

    @pytest.mark.asyncio
    async def test_mvp_generates_production_architecture(self):
        """Test MVP phase generates production-ready architecture."""
        # Arrange
        from tools.architecture_tool import generate_architecture_diagram
        
        with patch('tools.architecture_tool._get_chat_client') as mock_client:
            mock_openai = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps({
                "project_name": "MVP Project",
                "architecture_style": "microservices",
                "groups": [
                    {"id": "frontend", "label": "Frontend"},
                    {"id": "backend", "label": "Backend"},
                    {"id": "data", "label": "Data"},
                    {"id": "infra", "label": "Infrastructure"}
                ],
                "nodes": [
                    {"id": "cdn", "label": "Azure CDN", "groupId": "frontend"},
                    {"id": "apim", "label": "API Management", "groupId": "backend"},
                    {"id": "aks", "label": "AKS Cluster", "groupId": "backend"},
                    {"id": "sql", "label": "Azure SQL", "groupId": "data"},
                    {"id": "redis", "label": "Redis Cache", "groupId": "data"},
                    {"id": "monitor", "label": "Azure Monitor", "groupId": "infra"}
                ],
                "edges": [
                    {"source": "cdn", "target": "apim"},
                    {"source": "apim", "target": "aks"},
                    {"source": "aks", "target": "sql"},
                    {"source": "aks", "target": "redis"}
                ]
            })
            mock_openai.chat.completions.create.return_value = mock_response
            mock_client.return_value = mock_openai
            
            # Act
            result = await generate_architecture_diagram(
                context="Enterprise application",
                instructions="Create production architecture",
                phase_type="mvp"
            )
            
            # Assert
            assert result["phase_type"] == "mvp"
            assert result["phase_label"] == "MVP"
            assert len(result["graph"]["groups"]) >= 3  # MVP should have multiple tiers
            assert len(result["graph"]["nodes"]) >= 5  # MVP should have more components
