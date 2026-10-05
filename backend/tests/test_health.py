"""Initial test suite for backend health and status endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify that /api/health responds with healthy status and metadata."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "TouchGrass AI Backend"
    assert "version" in data


@pytest.mark.asyncio
async def test_ai_status_endpoint():
    """Verify that /api/ai-status responds without exposing secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/ai-status")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "model" in data
    assert "configured" in data
    assert data["fallback_available"] is True
    # Ensure no secrets leak
    assert "api_key" not in data
    assert "HOSTED_API_KEY" not in str(data)
