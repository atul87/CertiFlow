import pytest
import hmac
import hashlib
import json
from httpx import AsyncClient
from app.core.config import settings
from app.repositories.user_repository import UserRepository


def generate_mock_signature(payload_str: str) -> str:
    """Generate valid HMAC signature for mock billing webhook tests."""
    secret = settings.BILLING_WEBHOOK_SECRET
    return hmac.new(secret.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_get_plans_catalog(client: AsyncClient):
    """GET /api/v1/plans returns public plans catalog."""
    res = await client.get("/api/v1/plans")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "items" in data
    assert len(data["items"]) >= 5
    plan_names = [p["name"] for p in data["items"]]
    assert "Free Community" in plan_names
    assert "Starter" in plan_names
    assert "Professional" in plan_names


@pytest.mark.asyncio
async def test_subscription_lifecycle_and_checkout(client: AsyncClient, registered_user):
    """Test organization's initial trial and checkout initiation."""
    headers = registered_user["headers"]

    # 1. Fetch current subscription (should be in 14-day trial)
    sub_res = await client.get("/api/v1/subscription", headers=headers)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()["data"]
    assert sub_data["status"] == "trialing"
    assert sub_data["plan_id"] == "starter"
    assert sub_data["trial_end"] is not None

    # 2. Initiate checkout for Pro plan
    checkout_payload = {
        "plan_id": "pro",
        "billing_interval": "monthly",
        "success_url": "https://app.certiflow.io/billing?status=success",
        "cancel_url": "https://app.certiflow.io/billing?status=cancelled",
    }
    checkout_res = await client.post("/api/v1/subscription/checkout", json=checkout_payload, headers=headers)
    assert checkout_res.status_code == 200
    checkout_data = checkout_res.json()["data"]
    assert "checkout_url" in checkout_data
    assert "session_id" in checkout_data


@pytest.mark.asyncio
async def test_billing_webhooks_and_idempotency(client: AsyncClient, registered_user):
    """Test webhook processing, signature verification, and idempotency."""
    org_id = registered_user["organization"]["id"]

    # 1. Simulate checkout.completed event
    checkout_event = {
        "id": "evt_test_checkout_1001",
        "type": "checkout.completed",
        "data": {
            "organization_id": org_id,
            "plan_id": "pro",
            "provider_customer_id": f"cus_mock_{org_id}",
            "provider_subscription_id": f"sub_mock_{org_id}",
        }
    }
    payload_str = json.dumps(checkout_event)
    sig = generate_mock_signature(payload_str)

    res = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=payload_str,
        headers={"Content-Type": "application/json", "X-Mock-Signature": sig}
    )
    assert res.status_code == 200
    assert res.json()["data"]["received"] is True

    # Verify subscription is now active
    sub_res = await client.get("/api/v1/subscription", headers=registered_user["headers"])
    assert sub_res.status_code == 200
    assert sub_res.json()["data"]["status"] == "active"
    assert sub_res.json()["data"]["plan_id"] == "pro"

    # 2. Replay protection / Idempotency test
    # Re-sending the identical webhook must succeed without error or duplicate side-effects
    replay_res = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=payload_str,
        headers={"Content-Type": "application/json", "X-Mock-Signature": sig}
    )
    assert replay_res.status_code == 200
    assert replay_res.json()["data"]["duplicate"] is True

    # 3. Simulate invoice.paid event
    invoice_event = {
        "id": "evt_test_invoice_2002",
        "type": "invoice.paid",
        "data": {
            "organization_id": org_id,
            "provider_invoice_id": "in_mock_98765",
            "amount": 1999,
            "currency": "INR",
            "invoice_pdf_url": "https://billing.provider.test/invoices/in_mock_98765.pdf"
        }
    }
    inv_str = json.dumps(invoice_event)
    inv_sig = generate_mock_signature(inv_str)

    inv_webhook_res = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=inv_str,
        headers={"Content-Type": "application/json", "X-Mock-Signature": inv_sig}
    )
    assert inv_webhook_res.status_code == 200

    # Verify invoice appears in customer portal
    invoices_res = await client.get("/api/v1/billing/invoices", headers=registered_user["headers"])
    assert invoices_res.status_code == 200
    inv_list = invoices_res.json()["data"]["items"]
    assert len(inv_list) >= 1
    assert inv_list[0]["amount"] == 1999
    assert inv_list[0]["status"] == "paid"

    # 4. Simulate payment.failed event
    failed_event = {
        "id": "evt_test_failed_3003",
        "type": "payment.failed",
        "data": {
            "organization_id": org_id,
            "provider_invoice_id": "in_mock_fail_111",
            "amount": 1999,
        }
    }
    fail_str = json.dumps(failed_event)
    fail_sig = generate_mock_signature(fail_str)
    fail_res = await client.post(
        "/api/v1/billing/webhooks/mock",
        content=fail_str,
        headers={"Content-Type": "application/json", "X-Mock-Signature": fail_sig}
    )
    assert fail_res.status_code == 200

    # Subscription should now be past_due
    sub_past_due = await client.get("/api/v1/subscription", headers=registered_user["headers"])
    assert sub_past_due.json()["data"]["status"] == "past_due"


@pytest.mark.asyncio
async def test_usage_and_cost_endpoints(client: AsyncClient, registered_user):
    """Test customer billing usage summary and cost estimation endpoints."""
    headers = registered_user["headers"]

    # Usage summary
    usage_res = await client.get("/api/v1/billing/usage", headers=headers)
    assert usage_res.status_code == 200
    usage_data = usage_res.json()["data"]
    assert "period" in usage_data
    assert "metrics" in usage_data
    assert "certificates_generated" in usage_data["metrics"]

    # Cost estimate
    cost_res = await client.get("/api/v1/billing/cost-estimate", headers=headers)
    assert cost_res.status_code == 200
    cost_data = cost_res.json()["data"]
    assert "cost_breakdown" in cost_data
    assert "total_estimated_cost_inr" in cost_data


@pytest.mark.asyncio
async def test_cancellation_and_resumption(client: AsyncClient, registered_user):
    """Test customer scheduled cancellation at period end and resumption."""
    headers = registered_user["headers"]

    # Cancel at period end
    cancel_res = await client.post(
        "/api/v1/subscription/cancel",
        json={"reason": "Testing period end cancellation"},
        headers=headers
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["data"]["cancel_at_period_end"] is True

    # Resume subscription
    resume_res = await client.post("/api/v1/subscription/resume", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["data"]["cancel_at_period_end"] is False


@pytest.mark.asyncio
async def test_saas_admin_operations(client: AsyncClient, registered_user):
    """Test platform admin overview, plan override, and org suspension."""
    user = registered_user["user"]
    org_id = registered_user["organization"]["id"]

    # Elevate user to platform superadmin for test
    await UserRepository.update(user["id"], {"role": "superadmin"})

    headers = registered_user["headers"]

    # 1. Admin Platform Overview
    overview_res = await client.get("/api/v1/admin/overview", headers=headers)
    assert overview_res.status_code == 200
    overview_data = overview_res.json()["data"]
    assert "total_organizations" in overview_data
    assert "mrr" in overview_data
    assert "subscriptions_by_status" in overview_data

    # 2. Admin Manual Subscription Override
    override_res = await client.post(
        f"/api/v1/admin/organizations/{org_id}/subscription",
        json={"plan_id": "enterprise", "status": "active"},
        headers=headers
    )
    assert override_res.status_code == 200
    assert override_res.json()["data"]["plan_id"] == "enterprise"

    # 3. Admin Grant Temporary Promotional Entitlement
    grant_res = await client.post(
        f"/api/v1/admin/organizations/{org_id}/entitlements/grant",
        json={
            "metric": "max_certificates_monthly",
            "quantity": 10000,
            "reason": "VIP Conference sponsorship",
            "duration_days": 30
        },
        headers=headers
    )
    assert grant_res.status_code == 200
    assert grant_res.json()["data"]["quantity"] == 10000

    # 4. Admin Suspend and Restore Organization
    suspend_res = await client.post(
        f"/api/v1/admin/organizations/{org_id}/suspend",
        params={"reason": "Terms of service review"},
        headers=headers
    )
    assert suspend_res.status_code == 200
    assert suspend_res.json()["data"]["is_active"] is False

    restore_res = await client.post(
        f"/api/v1/admin/organizations/{org_id}/restore",
        headers=headers
    )
    assert restore_res.status_code == 200
    assert restore_res.json()["data"]["is_active"] is True
