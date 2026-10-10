import os
os.environ["APP_ENV"] = "test"

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.core.config import settings
from app.core.database import DatabaseManager
from app.main import app

settings.APP_ENV = "test"

TEST_DB_NAME = "certificate_platform_test"


@pytest_asyncio.fixture(autouse=True)
async def test_db_lifecycle(request):
    """Manage database connection and clean collections for each test.
    
    Tests marked with @pytest.mark.no_db skip the DB lifecycle entirely.
    Use this marker for pure unit tests that have no MongoDB dependencies.
    """
    # Skip DB setup/teardown for no_db marked tests
    if request.node.get_closest_marker("no_db"):
        yield
        return

    original_db = settings.MONGODB_DATABASE
    original_env = settings.APP_ENV
    settings.MONGODB_DATABASE = TEST_DB_NAME
    settings.APP_ENV = "test"
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
        settings.MONGODB_DATABASE = original_db
        settings.APP_ENV = original_env


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
    # Clear ambient cookies on test client so explicit unauth and header-based tests run cleanly
    client.cookies.clear()
    return {
        "user": data["user"],
        "organization": data["organization"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "raw_payload": payload
    }
