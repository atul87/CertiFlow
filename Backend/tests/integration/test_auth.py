import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    payload = {
        "name": "Jane Doe",
        "email": "janedoe@example.com",
        "password": "SecurePassword123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    data = body["data"]

    # Verify token fields
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    # Verify user fields
    user = data["user"]
    assert user["name"] == "Jane Doe"
    assert user["email"] == "janedoe@example.com"
    assert "id" in user
    assert "created_at" in user
    # Critical security check: password & password_hash must never be in responses
    assert "password" not in user
    assert "password_hash" not in user

    # Verify organization automatically created
    org = data["organization"]
    assert org["name"] == "Jane Doe's Organization"
    assert org["slug"] == "jane-does-organization"
    assert org["owner_id"] == user["id"]


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client: AsyncClient, registered_user):
    payload = {
        "name": "Duplicate User",
        "email": registered_user["raw_payload"]["email"],
        "password": "AnotherPassword123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DUPLICATE_EMAIL"


@pytest.mark.asyncio
async def test_register_invalid_email_rejected(client: AsyncClient):
    payload = {
        "name": "Invalid Email",
        "email": "not-an-email",
        "password": "ValidPassword123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client: AsyncClient):
    # Too short (< 8 chars)
    response1 = await client.post("/api/v1/auth/register", json={
        "name": "Weak Pass",
        "email": "weak1@example.com",
        "password": "pass"
    })
    assert response1.status_code == 422

    # Only letters, no numbers
    response2 = await client.post("/api/v1/auth/register", json={
        "name": "Weak Pass",
        "email": "weak2@example.com",
        "password": "passwordonlyletters"
    })
    assert response2.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user):
    payload = {
        "email": registered_user["raw_payload"]["email"],
        "password": registered_user["raw_payload"]["password"]
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client: AsyncClient, registered_user):
    payload = {
        "email": registered_user["raw_payload"]["email"],
        "password": "WrongPassword999"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_nonexistent_email_rejected(client: AsyncClient):
    payload = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_auth_me_requires_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_auth_me_authenticated(client: AsyncClient, registered_user):
    response = await client.get("/api/v1/auth/me", headers=registered_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["user"]["email"] == registered_user["user"]["email"]
    assert data["organization"]["id"] == registered_user["organization"]["id"]
    assert data["role"] == "owner"


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, registered_user):
    refresh_token = registered_user["refresh_token"]

    # 1. Successfully refresh
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    new_access = body["data"]["access_token"]
    new_refresh = body["data"]["refresh_token"]

    assert new_access != registered_user["access_token"]
    assert new_refresh != refresh_token

    # 2. Re-using the old refresh token must fail (it has been revoked/rotated)
    response_reuse = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response_reuse.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient, registered_user):
    refresh_token = registered_user["refresh_token"]

    # Logout with refresh token
    response = await client.post(
        "/api/v1/auth/logout",
        headers=registered_user["headers"],
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200

    # Refresh token should now be revoked
    refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 401
