import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.config import settings
from app.core.database import DatabaseManager
from app.main import app

TEST_DB_NAME = "certificate_platform_test"


@pytest_asyncio.fixture(autouse=True)
async def test_db_lifecycle():
    """Manage database connection and clean collections for each test."""
    settings.MONGODB_DATABASE = TEST_DB_NAME
    await DatabaseManager.connect()
    try:
        if DatabaseManager.db is not None:
            colls = await DatabaseManager.db.list_collection_names()
            for c in colls:
                if not c.startswith("system.") and c != "fonts":
                    await DatabaseManager.db[c].delete_many({})
        yield
    finally:
        await DatabaseManager.close()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "StrongPassword123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    return {
        "user": data["user"],
        "organization": data["organization"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "raw_payload": payload
    }
