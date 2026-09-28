import pytest
import hmac
import hashlib
import json
from httpx import AsyncClient
from app.repositories.usage_counter_repository import UsageCounterRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.usage_service import UsageService
from app.core.config import settings


@pytest.mark.asyncio
async def test_unauthenticated_billing_access_rejected(client: AsyncClient):
    """Anonymous access to subscription and billing endpoints must return 401."""
    res1 = await client.get("/api/v1/subscription")
    assert res1.status_code == 401

    res2 = await client.get("/api/v1/billing/invoices")
    assert res2.status_code == 401

    res3 = await client.get("/api/v1/billing/usage")
    assert res3.status_code == 401


@pytest.mark.asyncio
async def test_webhook_signature_forgery_rejected(client: AsyncClient):
    """Webhooks with missing, forged, or invalid HMAC signatures must return 401."""
    payload = json.dumps({"id": "evt_forged_999", "type": "checkout.completed", "data": {}})

    # Missing signature header
    res_no_sig = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=payload,
        headers={"Content-Type": "application/json"}
    )
    assert res_no_sig.status_code == 401

    # Forged signature
    res_bad_sig = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=payload,
        headers={"Content-Type": "application/json", "X-Mock-Signature": "invalid_forged_signature_hex"}
    )
    assert res_bad_sig.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoints_forbidden_for_regular_users(client: AsyncClient, registered_user):
    """Standard organization users cannot access platform superadmin endpoints (403 Forbidden)."""
    headers = registered_user["headers"]

    res_overview = await client.get("/api/v1/admin/overview", headers=headers)
    assert res_overview.status_code == 403

    res_override = await client.post(
        f"/api/v1/admin/organizations/{registered_user['organization']['id']}/subscription",
        json={"plan_id": "enterprise"},
        headers=headers
    )
    assert res_override.status_code == 403


@pytest.mark.asyncio
async def test_plan_tampering_rejected(client: AsyncClient, registered_user):
    """Checkout requests with non-existent or manipulated plans are rejected."""
    headers = registered_user["headers"]

    tampered_checkout = {
        "plan_id": "non_existent_hacked_plan",
        "billing_interval": "monthly"
    }
    res = await client.post("/api/v1/subscription/checkout", json=tampered_checkout, headers=headers)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_hard_quota_enforcement_blocks_certificate_generation(client: AsyncClient, registered_user):
    """Organizations that exceed their monthly certificate quota are rejected with 403 Forbidden."""
    org_id = registered_user["organization"]["id"]
    headers = registered_user["headers"]
    period = UsageService.current_period()

    # Move organization to Free Community plan (100 certificates limit)
    await SubscriptionRepository.upsert_subscription(
        org_id=org_id,
        plan_id="free",
        status="active"
    )

    # Exhaust quota by setting usage counter to 100
    await UsageCounterRepository.set_counter(org_id, "certificates_generated", period, 100)

    # Attempt to generate a certificate via service check
    from app.services.quota_service import QuotaService
    from app.core.exceptions import ForbiddenError

    with pytest.raises(ForbiddenError) as exc_info:
        await QuotaService.check_certificate_quota(org_id=org_id, quantity=1)
    assert exc_info.value.code == "CERTIFICATE_QUOTA_EXCEEDED"
    assert "Please upgrade your plan" in str(exc_info.value.message)
