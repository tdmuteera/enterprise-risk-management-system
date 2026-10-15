"""
Basic tests for ERM Platform health and configuration.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API info."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "db" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_api_info_endpoint():
    """Test API info endpoint."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert data["api_version"] == "v1"


@pytest.mark.asyncio
async def test_swagger_docs():
    """Test Swagger documentation is available."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_redoc_docs():
    """Test ReDoc documentation is available."""
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/redoc")
        assert response.status_code == 200
