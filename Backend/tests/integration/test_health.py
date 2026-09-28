import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "certificate-api"
    assert "version" in data
    # Verify X-Request-ID header attached by middleware
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"].startswith("req_")


@pytest.mark.asyncio
async def test_api_v1_health(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "certificate-api"


@pytest.mark.asyncio
async def test_api_v1_health_db(client: AsyncClient):
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
