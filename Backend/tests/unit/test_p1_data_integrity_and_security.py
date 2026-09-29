"""
Unit and regression tests for P1 — Data Integrity, Multi-Tenancy & Security:
Item 8:  MongoDB transaction scope boundary
Item 9:  Strict re-checking of organization membership on every authenticated request
Item 10: JWT JTI revocation and blacklist check
Item 11 & 12: Consolidated rate limiter with fail-closed vs fail-open modes
Item 13: Canonical vs deprecated verification endpoint contracts
"""
from __future__ import annotations
import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import create_access_token
from app.core.database import DatabaseManager
from app.security.token_blacklist import TokenBlacklist
from app.services.rate_limiter import RateLimiter, APIRateLimiter
from app.api.deps import get_current_user_and_org


# ---------------------------------------------------------------------------
# 1. Item 8: Transaction Scope Boundary
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_database_manager_transaction_scope_yields_session():
    """Verify transaction_scope enters session and commits or handles standalone mode."""
    async with DatabaseManager.transaction_scope() as session:
        # In test/standalone environment, session is yielded cleanly (either client session or fallback)
        pass


# ---------------------------------------------------------------------------
# 2. Item 9: Strict Organization Membership Re-Checking on Every Request
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_recheck_membership_blocks_removed_or_suspended_members():
    """If user membership becomes removed or suspended, access must be denied with 403."""
    user_id = str(ObjectId())
    org_id = str(ObjectId())
    token = create_access_token(user_id=user_id, org_id=org_id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = MagicMock()

    mock_user = {"id": user_id, "email": "test@org.com", "is_active": True}
    mock_org = {"id": org_id, "name": "Test Org", "status": "active", "owner_id": str(ObjectId())}

    with patch("app.repositories.user_repository.UserRepository.get_by_id", new_callable=AsyncMock) as mock_u:
        mock_u.return_value = mock_user
        with patch("app.repositories.organization_repository.OrganizationRepository.get_by_id", new_callable=AsyncMock) as mock_o:
            mock_o.return_value = mock_org
            with patch("app.repositories.member_repository.MemberRepository.get_by_user_id", new_callable=AsyncMock) as mock_m:
                # 1. Suspended member
                mock_m.return_value = {"status": "suspended", "role": "member"}
                with pytest.raises(ForbiddenError) as exc_info:
                    await get_current_user_and_org(request, credentials=credentials)
                assert exc_info.value.code == "MEMBER_SUSPENDED"

                # 2. Removed member
                mock_m.return_value = {"status": "removed", "role": "member"}
                with pytest.raises(ForbiddenError) as exc_info:
                    await get_current_user_and_org(request, credentials=credentials)
                assert exc_info.value.code == "MEMBER_REMOVED"


@pytest.mark.asyncio
async def test_recheck_membership_blocks_alien_header_organization():
    """If caller passes X-Organization-Id for an org they do not belong to, reject with 403."""
    user_id = str(ObjectId())
    token_org_id = str(ObjectId())
    alien_org_id = str(ObjectId())
    token = create_access_token(user_id=user_id, org_id=token_org_id)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = MagicMock()

    mock_user = {"id": user_id, "email": "test@org.com", "is_active": True}
    alien_org = {"id": alien_org_id, "name": "Alien Org", "status": "active", "owner_id": str(ObjectId())}

    with patch("app.repositories.user_repository.UserRepository.get_by_id", new_callable=AsyncMock) as mock_u:
        mock_u.return_value = mock_user
        with patch("app.repositories.organization_repository.OrganizationRepository.get_by_id", new_callable=AsyncMock) as mock_o:
            mock_o.return_value = alien_org
            with patch("app.repositories.member_repository.MemberRepository.get_by_user_id", new_callable=AsyncMock) as mock_m:
                mock_m.return_value = None  # Not a member of alien org
                with pytest.raises(ForbiddenError) as exc_info:
                    await get_current_user_and_org(request, credentials=credentials, x_organization_id=alien_org_id)
                assert exc_info.value.code == "NOT_A_MEMBER"


# ---------------------------------------------------------------------------
# 3. Item 10: JWT Revocation & JTI Blacklist
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_jwt_jti_revocation_blacklist():
    """Blacklisted JTI tokens must be immediately rejected with 401 TOKEN_REVOKED."""
    TokenBlacklist.clear_in_memory()
    user_id = str(ObjectId())
    org_id = str(ObjectId())

    # Generate token
    token = create_access_token(user_id=user_id, org_id=org_id)
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    jti = payload["jti"]

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = MagicMock()

    # Pre-revocation check: token is valid
    assert await TokenBlacklist.is_jti_revoked(jti) is False

    # Revoke JTI
    await TokenBlacklist.revoke_jti(jti, ttl_seconds=60)
    assert await TokenBlacklist.is_jti_revoked(jti) is True

    # Attempt request with revoked token
    with pytest.raises(UnauthorizedError) as exc_info:
        await get_current_user_and_org(request, credentials=credentials)
    assert exc_info.value.code == "TOKEN_REVOKED"

    TokenBlacklist.clear_in_memory()


# ---------------------------------------------------------------------------
# 4. Item 11 & 12: Consolidated Rate Limiter & Fail-Closed / Fail-Open
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rate_limiter_in_memory_sliding_window_enforcement():
    """Verify consolidated rate limiter enforces rate limits in-memory when Redis is bypassed."""
    RateLimiter.clear_in_memory()
    key = "test_user_rate_limit_key"

    # Allow up to 3 requests
    assert await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60) is True
    assert await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60) is True
    assert await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60) is True

    # 4th request must be rejected
    assert await RateLimiter.is_allowed(key, max_requests=3, window_seconds=60) is False

    # Detailed status verification
    allowed, limit, remaining, retry_after = await RateLimiter.check_rate_limit(
        identifier=key, limit_per_minute=3, window_seconds=60
    )
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0

    RateLimiter.clear_in_memory()


@pytest.mark.asyncio
async def test_rate_limiter_api_alias_backward_compatibility():
    """Verify APIRateLimiter alias exposes identical check_rate_limit API."""
    RateLimiter.clear_in_memory()
    key = "test_api_key_quota"

    allowed, limit, remaining, retry_after = await APIRateLimiter.check_rate_limit(
        identifier=key, limit_per_minute=5
    )
    assert allowed is True
    assert limit == 5
    assert remaining == 4
    assert retry_after == 0

    RateLimiter.clear_in_memory()


# ---------------------------------------------------------------------------
# 5. Item 13: Deprecation Header on Legacy Verification Route
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_legacy_verify_route_includes_deprecation_headers():
    """Calling /api/v1/certificates/verify/{code} returns Deprecation & Link headers."""
    from fastapi import Response
    from app.api.v1.certificates import verify_certificate
    from app.schemas.verification import PublicVerificationResponse, PublicCertificateDetail

    mock_resp = Response()
    request = MagicMock()
    request.headers = {}
    request.client.host = "127.0.0.1"

    fake_cert = PublicCertificateDetail(
        certificate_number="CERT-2026-0001",
        recipient_name="Alice Smith",
        program_name="AI Masterclass",
    )
    from datetime import datetime, timezone
    fake_result = PublicVerificationResponse(
        valid=True,
        status="valid",
        verified_at=datetime.now(timezone.utc),
        certificate=fake_cert,
    )

    with patch("app.services.verification_service.VerificationService.verify_by_code", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = fake_result
        res = await verify_certificate(code="VCODE-TEST", request=request, response=mock_resp)

        assert res.valid is True
        assert mock_resp.headers.get("Deprecation") == "@true"
        assert "/api/v1/public/verify/VCODE-TEST" in mock_resp.headers.get("Link", "")
