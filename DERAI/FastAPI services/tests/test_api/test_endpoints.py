"""Tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Health endpoint should return 200 with service status."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "services" in data


@pytest.mark.asyncio
async def test_health_no_auth_required(async_client):
    """Health endpoint should be accessible without API key."""
    from httpx import ASGITransport, AsyncClient
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_process_single_requires_auth():
    """Protected endpoints should reject requests without API key."""
    from httpx import ASGITransport, AsyncClient
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/process-single", json={})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_compare_results_empty(async_client):
    """Compare results should return empty list initially."""
    response = await async_client.get("/api/v1/compare-results")
    assert response.status_code == 200
    assert response.json() == []
