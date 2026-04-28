"""
Unit Tests for Cost Report Tool Module
Using AAA (Arrange, Act, Assert) Pattern

Tests cover:
- parse_phase_selection
- get_phase_selection_message
- generate_cost_report
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json


class TestParsePhaseSelection:
    """Unit tests for parse_phase_selection function."""

    def test_parse_phase_selection_poc_lowercase(self):
        """Test parsing 'poc' input."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "poc"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "poc"

    def test_parse_phase_selection_poc_uppercase(self):
        """Test parsing 'POC' input."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "POC"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "poc"

    def test_parse_phase_selection_number_1(self):
        """Test parsing '1' for POC."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "1"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "poc"

    def test_parse_phase_selection_mvp_lowercase(self):
        """Test parsing 'mvp' input."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "mvp"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "mvp"

    def test_parse_phase_selection_number_2(self):
        """Test parsing '2' for MVP."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "2"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "mvp"

    def test_parse_phase_selection_both(self):
        """Test parsing 'both' input."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "both"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "both"

    def test_parse_phase_selection_number_3(self):
        """Test parsing '3' for both."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "3"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "both"

    def test_parse_phase_selection_comparison(self):
        """Test parsing 'comparison' returns both."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "comparison"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "both"

    def test_parse_phase_selection_unknown_defaults_to_both(self):
        """Test unknown input defaults to 'both'."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "unknown option"
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "both"

    def test_parse_phase_selection_with_whitespace(self):
        """Test parsing input with extra whitespace."""
        # Arrange
        from tools.cost_report_tool import parse_phase_selection
        user_input = "  POC  "
        
        # Act
        result = parse_phase_selection(user_input)
        
        # Assert
        assert result == "poc"


class TestGetPhaseSelectionMessage:
    """Unit tests for get_phase_selection_message function."""

    def test_get_phase_selection_message_returns_string(self):
        """Test that phase selection message is returned."""
        # Arrange
        from tools.cost_report_tool import get_phase_selection_message
        
        # Act
        result = get_phase_selection_message()
        
        # Assert
        assert isinstance(result, str)
        assert len(result) > 0


class TestGenerateCostReport:
    """Unit tests for generate_cost_report function."""

    @pytest.mark.asyncio
    @patch('tools.cost_report_tool._get_chat_client')
    @patch('tools.cost_report_tool.generate_cost_excel')
    @patch('tools.cost_report_tool.upload_bytes')
    async def test_generate_cost_report_poc_success(
        self, mock_upload, mock_excel, mock_client
    ):
        """Test generating POC cost report successfully."""
        # Arrange
        from tools.cost_report_tool import generate_cost_report
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "report_title": "Azure Cost Estimate",
            "poc": {
                "services": [
                    {"service_name": "Azure App Service", "monthly_cost": 50.00}
                ],
                "total_monthly": 50.00
            }
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        mock_excel.return_value = b"excel file bytes"
        mock_upload.return_value = ("https://blob.url/report.xlsx", "path/report.xlsx")
        
        context = "Project needs Azure App Service"
        instructions = "Generate cost estimate"
        
        # Act
        result = await generate_cost_report(context, instructions, phase_type="poc")
        
        # Assert
        assert "download_url" in result or "excel_url" in result or mock_upload.called

    @pytest.mark.asyncio
    @patch('tools.cost_report_tool._get_chat_client')
    @patch('tools.cost_report_tool.generate_cost_excel')
    @patch('tools.cost_report_tool.upload_bytes')
    async def test_generate_cost_report_mvp_success(
        self, mock_upload, mock_excel, mock_client
    ):
        """Test generating MVP cost report successfully."""
        # Arrange
        from tools.cost_report_tool import generate_cost_report
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "report_title": "Azure Cost Estimate",
            "mvp": {
                "services": [
                    {"service_name": "Azure App Service", "monthly_cost": 200.00},
                    {"service_name": "Azure SQL", "monthly_cost": 150.00}
                ],
                "total_monthly": 350.00
            }
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        mock_excel.return_value = b"excel file bytes"
        mock_upload.return_value = ("https://blob.url/report.xlsx", "path/report.xlsx")
        
        context = "Project needs production-ready infrastructure"
        instructions = "Generate MVP cost estimate"
        
        # Act
        result = await generate_cost_report(context, instructions, phase_type="mvp")
        
        # Assert
        assert mock_openai.chat.completions.create.called

    @pytest.mark.asyncio
    @patch('tools.cost_report_tool._get_chat_client')
    @patch('tools.cost_report_tool.generate_cost_excel')
    @patch('tools.cost_report_tool.upload_bytes')
    async def test_generate_cost_report_both_phases(
        self, mock_upload, mock_excel, mock_client
    ):
        """Test generating cost report with both POC and MVP."""
        # Arrange
        from tools.cost_report_tool import generate_cost_report
        
        mock_openai = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "report_title": "Azure Cost Comparison",
            "poc": {
                "services": [{"service_name": "App Service", "monthly_cost": 50.00}],
                "total_monthly": 50.00
            },
            "mvp": {
                "services": [{"service_name": "App Service Premium", "monthly_cost": 200.00}],
                "total_monthly": 200.00
            }
        })
        mock_openai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_openai
        
        mock_excel.return_value = b"excel file bytes"
        mock_upload.return_value = ("https://blob.url/report.xlsx", "path/report.xlsx")
        
        context = "Compare POC vs MVP costs"
        instructions = "Generate comparison report"
        
        # Act
        result = await generate_cost_report(context, instructions, phase_type="both")
        
        # Assert
        assert mock_openai.chat.completions.create.called
