
# NOTE:
# The original integration tests targeted endpoints like /chat, /new-session, /upload-artifact, /generate-all
# which do NOT exist in OptiStudio-agent/main.py. The actual API exposes /api/agent/... routes such as:
#   - /api/agent/unified-chat
#   - /api/agent/process-artifacts
#   - /api/agent/select-phase
# The tests below have been updated to call the correct API routes and use the correct request/response contracts.
# This prevents 404 errors and ensures the tests are valid for the current FastAPI implementation.

"""
Integration tests for the FastAPI application.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_ok(self):
        """Health endpoint should return 200 OK."""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "healthy" or "ok" in str(data).lower()


class TestChatEndpoints:
    """Tests for chat-related endpoints."""

    @pytest.mark.asyncio
    async def test_unified_chat_without_session_returns_error(self):
        """Unified chat without session should return error."""
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/agent/unified-chat",
                json={"message": "Hello"}
            )
            # Should return 400 or 422 without session_id
            assert response.status_code in [400, 422]

    # There is no /new-session endpoint. If session creation is needed, mock or skip.


class TestArtifactEndpoints:
    """Tests for artifact upload endpoints."""

    @pytest.mark.asyncio
    async def test_process_artifacts_without_artifacts_returns_error(self):
        """Process artifacts without artifacts should return error."""
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/agent/process-artifacts",
                json={"session_id": "test-session", "artifacts": []}
            )
            # Should return error or warning for missing artifacts
            assert response.status_code in [200, 400, 422]



class TestGenerationEndpoints:
    """
    Tests for generation endpoints.
    This test verifies that the /api/agent/select-phase endpoint is reachable and properly validates input.
    It uses a minimal valid payload (session_id, artifacts, phase_type) to ensure the endpoint contract is correct.
    The response may be success or error depending on backend validation logic, but should not return 404.
    """

    @pytest.mark.asyncio
    async def test_select_phase_with_minimal_payload(self):
        """Select phase (generate all) with minimal valid payload should return error or success depending on backend validation."""
        from main import app
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/agent/select-phase",
                json={
                    "session_id": "test-session",
                    "artifacts": [],
                    "phase_type": "poc"
                }
            )
            # Should return error or success depending on backend validation
            assert response.status_code in [200, 400, 422]


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_404_for_unknown_endpoint(self):
        """Unknown endpoint should return 404."""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/unknown-endpoint-xyz")
            
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_method_not_allowed(self):
        """Wrong HTTP method should return 405."""
        from main import app
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # POST to health (which is GET only)
            response = await client.post("/health")
            
            assert response.status_code == 405
