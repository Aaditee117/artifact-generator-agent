"""
Unit Tests for Agent Dispatcher Module
            "success": True,
            "toon_response": large_response
        }
        
        tool_name = "execute_admin_sql"
        arguments = json.dumps({"query": "SELECT * FROM BigTable"})
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert len(result) < len(large_response)
        assert "[truncated]" in result
        assert len(toon) == 2000  # Full response in toon


class TestDispatchToolCallQueryUnstructuredData:
    """Unit tests for dispatch_tool_call with query_unstructured_data."""

    @pytest.mark.asyncio
    @patch('tools.agent_dispatcher.query_unstructured_data')
    async def test_dispatch_query_unstructured_data_success(self, mock_query):
        """Test dispatching query_unstructured_data successfully."""
        # Arrange
        from tools.agent_dispatcher import dispatch_tool_call
        
        mock_query.return_value = {
            "success": True,
            "response": "The architecture uses microservices pattern with Azure services."
        }
        
        tool_name = "query_unstructured_data"
        arguments = json.dumps({"search_query": "What is the architecture pattern?"})
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert "microservices" in result
        assert sql is None
        assert toon is None

    @pytest.mark.asyncio
    @patch('tools.agent_dispatcher.query_unstructured_data')
    async def test_dispatch_query_unstructured_data_error(self, mock_query):
        """Test dispatching query_unstructured_data with error."""
        # Arrange
        from tools.agent_dispatcher import dispatch_tool_call
        
        mock_query.return_value = {
            "success": False,
            "error": "Search index not available"
        }
        
        tool_name = "query_unstructured_data"
        arguments = json.dumps({"search_query": "test query"})
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert "RAG Error" in result
        assert "Search index not available" in result


class TestDispatchToolCallUnknownTool:
    """Unit tests for dispatch_tool_call with unknown tools."""

    @pytest.mark.asyncio
    async def test_dispatch_unknown_tool(self):
        """Test dispatching unknown tool returns error."""
        # Arrange
        from tools.agent_dispatcher import dispatch_tool_call
        
        tool_name = "unknown_tool"
        arguments = "{}"
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert "Unknown tool" in result
        assert "unknown_tool" in result
        assert sql is None
        assert toon is None


class TestDispatchToolCallParsingErrors:
    """Unit tests for dispatch_tool_call argument parsing errors."""

    @pytest.mark.asyncio
    async def test_dispatch_invalid_json_arguments(self):
        """Test dispatching with invalid JSON arguments."""
        # Arrange
        from tools.agent_dispatcher import dispatch_tool_call
        
        tool_name = "execute_admin_sql"
        arguments = "not valid json {"
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert "Tool Parsing Error" in result

    @pytest.mark.asyncio
    async def test_dispatch_empty_arguments(self):
        """Test dispatching with empty arguments string."""
        # Arrange
        from tools.agent_dispatcher import dispatch_tool_call
        
        tool_name = "execute_admin_sql"
        arguments = ""
        
        # Act
        result, sql, toon = await dispatch_tool_call(tool_name, arguments)
        
        # Assert
        assert "Error" in result


class TestAgentTools:
    """Unit tests for AGENT_TOOLS configuration."""

    def test_agent_tools_has_required_tools(self):
        """Test AGENT_TOOLS contains all required tools."""
        # Arrange
        from tools.agent_dispatcher import AGENT_TOOLS
        
        expected_tools = ["get_database_schema", "execute_admin_sql", "query_unstructured_data"]
        
        # Act
        tool_names = [t["function"]["name"] for t in AGENT_TOOLS]
        
        # Assert
        for expected in expected_tools:
            assert expected in tool_names

    def test_agent_tools_have_descriptions(self):
        """Test all AGENT_TOOLS have descriptions."""
        # Arrange
        from tools.agent_dispatcher import AGENT_TOOLS
        
        # Act & Assert
        for tool in AGENT_TOOLS:
            assert "description" in tool["function"]
            assert len(tool["function"]["description"]) > 10

    def test_agent_tools_have_parameters(self):
        """Test all AGENT_TOOLS have parameter definitions."""
        # Arrange
        from tools.agent_dispatcher import AGENT_TOOLS
        
        # Act & Assert
        for tool in AGENT_TOOLS:
            assert "parameters" in tool["function"]
            assert "type" in tool["function"]["parameters"]
            assert tool["function"]["parameters"]["type"] == "object"
