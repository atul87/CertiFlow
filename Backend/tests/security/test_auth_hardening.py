import pytest
from httpx import AsyncClient
from app.services.auth_service import AuthService
from app.core.exceptions import UnauthorizedError


@pytest.mark.asyncio
async def test_forgot_password_account_enumeration_protection(client: AsyncClient, registered_user):
    """
    Ensure POST /auth/forgot-password returns the exact same generic success message
    regardless of whether the email exists in the database.
    """
    # 1. Existing user
    resp_existing = await client.post("/api/v1/auth/forgot-password", json={
        "email": registered_user["user"]["email"]
    })
    assert resp_existing.status_code == 200
    data_existing = resp_existing.json()["data"]
    assert "If this email is registered, password reset instructions have been sent." in data_existing["message"]
    # In test mode, reset_token is provided for test assertions
    token = data_existing.get("reset_token")
    assert token is not None

    # 2. Non-existent user
    resp_nonexistent = await client.post("/api/v1/auth/forgot-password", json={
        "email": "nonexistent_ghost_user@example.com"
    })
    assert resp_nonexistent.status_code == 200
    data_nonexistent = resp_nonexistent.json()["data"]
    # Identical message protects against user enumeration
    assert data_nonexistent["message"] == data_existing["message"]
    assert data_nonexistent.get("reset_token") is None


@pytest.mark.asyncio
async def test_password_reset_flow_and_session_invalidation(client: AsyncClient, registered_user):
    """
    Test complete reset cycle:
    1. Request reset token
    2. Reset password
    3. Old password fails, new password succeeds
    4. Previous refresh token is revoked
    5. Reused reset token is rejected
    """
    email = registered_user["user"]["email"]
    old_password = registered_user["raw_payload"]["password"]
    new_password = "BrandNewSecurePassword456!"
    old_refresh_token = registered_user["refresh_token"]

    # 1. Request reset token
    req_resp = await client.post("/api/v1/auth/forgot-password", json={"email": email})
    token = req_resp.json()["data"]["reset_token"]
    assert token is not None

    # 2. Execute password reset
    reset_resp = await client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": new_password
    })
    assert reset_resp.status_code == 200
    assert reset_resp.json()["success"] is True

    # 3. Old password must fail
    old_login = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": old_password
    })
    assert old_login.status_code == 401

    # 4. New password must succeed
    new_login = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": new_password
    })
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()["data"]

    # 5. Old refresh token was revoked upon password reset
    refresh_attempt = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh_token
    })
    assert refresh_attempt.status_code == 401

    # 6. Reusing the reset token must be rejected (single-use guarantee)
    reuse_resp = await client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": "YetAnotherPassword789!"
    })
    assert reuse_resp.status_code == 422
    assert reuse_resp.json()["error"]["code"] == "INVALID_RESET_TOKEN"


@pytest.mark.asyncio
async def test_reauthentication_validation(registered_user):
    """
    Test re-authentication verification helper.
    """
    user_id = registered_user["user"]["id"]
    password = registered_user["raw_payload"]["password"]

    # Valid password
    is_valid = await AuthService.verify_reauth(user_id=user_id, password=password)
    assert is_valid is True

    # Invalid password raises UnauthorizedError
    with pytest.raises(UnauthorizedError) as exc_info:
        await AuthService.verify_reauth(user_id=user_id, password="WrongPassword999")
    assert exc_info.value.code == "REAUTH_REQUIRED"
