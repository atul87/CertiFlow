import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository


@pytest.mark.asyncio
async def test_cookie_session_authentication(client: AsyncClient):
    """Verify registration sets HttpOnly access/refresh cookies and client-readable CSRF cookie."""
    client.cookies.clear()
    payload = {
        "name": "Cookie User",
        "email": "cookie_auth_user@example.com",
        "password": "SecurePassword123!"
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201

    # Check cookies were set by FastAPI
    cookies = client.cookies
    assert settings.COOKIE_ACCESS_NAME in cookies
    assert settings.COOKIE_REFRESH_NAME in cookies
    assert settings.COOKIE_CSRF_NAME in cookies

    # Make request to protected /auth/me with NO Authorization header — relies purely on HttpOnly cookie!
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    data = me_resp.json()["data"]
    assert data["user"]["email"] == "cookie_auth_user@example.com"


@pytest.mark.asyncio
async def test_cookie_csrf_enforcement_on_mutating_requests(client: AsyncClient):
    """Verify CSRF token is required and validated on state mutations when authenticated via cookies."""
    client.cookies.clear()
    login_payload = {
        "name": "CSRF Tester",
        "email": "csrf_tester@example.com",
        "password": "SecurePassword123!"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=login_payload)
    assert reg_resp.status_code == 201

    csrf_token = client.cookies.get(settings.COOKIE_CSRF_NAME)
    assert csrf_token is not None

    template_payload = {
        "name": "CSRF Certificate Template",
        "canvas": {"width": 800, "height": 600, "unit": "px", "dpi": 72},
        "elements": []
    }

    # 1. Mutating POST without X-CSRF-Token header must fail with 403 CSRF_TOKEN_MISSING
    no_csrf_resp = await client.post("/api/v1/templates", json=template_payload)
    assert no_csrf_resp.status_code == 403
    assert no_csrf_resp.json()["error"]["code"] == "CSRF_TOKEN_MISSING"

    # 2. Mutating POST with mismatched X-CSRF-Token header must fail with 403 CSRF_TOKEN_MISMATCH
    bad_csrf_resp = await client.post(
        "/api/v1/templates",
        json=template_payload,
        headers={"X-CSRF-Token": "invalid_forged_csrf_token_value_xyz"}
    )
    assert bad_csrf_resp.status_code == 403
    assert bad_csrf_resp.json()["error"]["code"] == "CSRF_TOKEN_MISMATCH"

    # 3. Mutating POST with correct X-CSRF-Token header matching cookie succeeds!
    good_csrf_resp = await client.post(
        "/api/v1/templates",
        json=template_payload,
        headers={"X-CSRF-Token": csrf_token}
    )
    assert good_csrf_resp.status_code == 201
    assert good_csrf_resp.json()["success"] is True

    # 4. Programmatic API access using Bearer token directly does not require CSRF
    bearer_token = reg_resp.json()["data"]["access_token"]
    # Clear cookies to simulate pure programmatic API client
    client.cookies.clear()
    bearer_resp = await client.post(
        "/api/v1/templates",
        json=template_payload,
        headers={"Authorization": f"Bearer {bearer_token}"}
    )
    assert bearer_resp.status_code == 201


@pytest.mark.asyncio
async def test_server_controlled_demo_auth_lifecycle(client: AsyncClient):
    """Verify demo-session endpoint works in dev/test but is blocked when ALLOW_DEMO_AUTH is disabled."""
    client.cookies.clear()

    # 1. In test environment with ALLOW_DEMO_AUTH enabled:
    demo_resp = await client.post("/api/v1/auth/demo-session")
    assert demo_resp.status_code == 200
    assert demo_resp.json()["success"] is True
    data = demo_resp.json()["data"]
    assert data["user"]["email"] == "demo@certiflow.io"
    assert settings.COOKIE_ACCESS_NAME in client.cookies

    # Access protected route using demo cookie session
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["user"]["email"] == "demo@certiflow.io"

    # 2. When ALLOW_DEMO_AUTH is disabled (or simulated in production):
    with patch.object(settings, "ALLOW_DEMO_AUTH", False):
        blocked_resp = await client.post("/api/v1/auth/demo-session")
        assert blocked_resp.status_code == 403
        assert blocked_resp.json()["error"]["code"] == "DEMO_AUTH_DISABLED"


@pytest.mark.asyncio
async def test_cookie_logout_clears_cookies(client: AsyncClient):
    """Verify logout revokes session and instructs browser to delete cookies."""
    client.cookies.clear()
    reg_resp = await client.post("/api/v1/auth/register", json={
        "name": "Logout Tester",
        "email": "logout_tester@example.com",
        "password": "SecurePassword123!"
    })
    assert reg_resp.status_code == 201
    csrf_token = client.cookies.get(settings.COOKIE_CSRF_NAME)

    # Logout with CSRF token
    logout_resp = await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert logout_resp.status_code == 200

    # Cookie jar should have deleted the cookies (value empty or max-age=0)
    # Testing unauth immediately afterwards
    unauth_resp = await client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401
