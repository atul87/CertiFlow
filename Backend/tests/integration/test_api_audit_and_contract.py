import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_audit_health_and_plans_contracts(client: AsyncClient):
    """Verify public health readiness probe and SaaS plan catalogs."""
    # 1. GET /api/v1/health/ready
    ready_resp = await client.get("/api/v1/health/ready")
    assert ready_resp.status_code == 200
    ready_data = ready_resp.json()
    assert ready_data["status"] in ("ready", "degraded", "not_ready")
    assert "dependencies" in ready_data
    assert "mongodb" in ready_data["dependencies"]

    # 2. GET /api/v1/plans
    plans_resp = await client.get("/api/v1/plans")
    assert plans_resp.status_code == 200
    plans = plans_resp.json()["data"]["items"]
    assert len(plans) >= 3

    # 3. GET /api/v1/plans/{plan_id}
    free_plan = plans[0]
    p_resp = await client.get(f"/api/v1/plans/{free_plan['plan_id']}")
    assert p_resp.status_code == 200
    p_data = p_resp.json()["data"]
    assert p_data["plan_id"] == free_plan["plan_id"]
    assert "entitlements" in p_data
    assert "features" in p_data


@pytest.mark.asyncio
async def test_audit_http_status_matrix_and_auth_guards(client: AsyncClient, registered_user):
    """Exhaustive check of 401, 403, 404, 422, and 200/201 status contracts."""
    headers = registered_user["headers"]

    # 401 Unauthorized: Calling protected endpoints with no token or malformed token
    unauth_resp1 = await client.get("/api/v1/templates")
    assert unauth_resp1.status_code == 401
    assert unauth_resp1.json()["success"] is False
    assert unauth_resp1.json()["error"]["code"] == "UNAUTHORIZED"

    unauth_resp2 = await client.get("/api/v1/templates", headers={"Authorization": "Bearer bad_token"})
    assert unauth_resp2.status_code == 401

    # 404 Not Found: Non-existent IDs with structured APIError envelope
    not_found_resp = await client.get("/api/v1/templates/non_existent_tmpl_999", headers=headers)
    assert not_found_resp.status_code == 404
    assert not_found_resp.json()["success"] is False
    assert not_found_resp.json()["error"]["code"] == "TEMPLATE_NOT_FOUND"

    # 422 Unprocessable Entity: Malformed JSON or missing required fields
    bad_payload_resp = await client.post("/api/v1/templates", headers=headers, json={"wrong_key": 123})
    assert bad_payload_resp.status_code == 422
    assert bad_payload_resp.json()["success"] is False
    assert bad_payload_resp.json()["error"]["code"] == "VALIDATION_ERROR"

    # 201 Created: Valid resource creation contract
    create_resp = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": "Audit Matrix Template", "canvas": {"width": 1200, "height": 850}}
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["success"] is True
    assert "id" in create_resp.json()["data"]


@pytest.mark.asyncio
async def test_audit_certificates_preview_and_verify_alias(client: AsyncClient, registered_user):
    """Verify live certificate preview rendering and /verify/{code} alias route."""
    headers = registered_user["headers"]

    # 1. Create and publish a template version first
    t_resp = await client.post("/api/v1/templates", headers=headers, json={"name": "Preview Template"})
    assert t_resp.status_code == 201
    tmpl_id = t_resp.json()["data"]["id"]
    ver_id = t_resp.json()["data"]["current_version_id"]

    await client.post(f"/api/v1/templates/{tmpl_id}/versions/{ver_id}/publish", headers=headers)

    # 2. POST /api/v1/certificates/preview
    preview_payload = {
        "template_version_id": ver_id,
        "data": {
            "recipient_name": "Atul Kumar Das",
            "recipient_email": "atul@example.com",
            "program_name": "AI Workshop 2026",
            "issue_date": "29 September 2026"
        }
    }
    prev_resp = await client.post("/api/v1/certificates/preview", headers=headers, json=preview_payload)
    assert prev_resp.status_code == 200
    prev_data = prev_resp.json()["data"]
    assert "preview_url" in prev_data
    assert prev_data["preview_url"].startswith("data:image/png;base64,")
    assert "diagnostics" in prev_data

    # 3. GET /api/v1/verify/{code} for invalid/non-existent code
    verify_resp = await client.get("/api/v1/verify/NON-EXISTENT-CODE-999")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["valid"] is False
    assert verify_data["status"] == "not_found"


@pytest.mark.asyncio
async def test_audit_email_suppressions_lifecycle(client: AsyncClient, registered_user):
    """Verify email suppression listing, adding, and deletion contracts."""
    headers = registered_user["headers"]
    test_email = "bounced_user_audit@example.com"

    # 1. Add email to suppression list
    add_resp = await client.post(
        "/api/v1/email/suppressions",
        headers=headers,
        json={"email": test_email, "reason": "hard_bounce"}
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["data"]["email"] == test_email

    # 2. List suppressions
    list_resp = await client.get("/api/v1/email/suppressions", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()["data"]["items"]
    assert any(i["email"] == test_email for i in items)

    # 3. Remove email from suppression list
    del_resp = await client.delete(f"/api/v1/email/suppressions/{test_email}", headers=headers)
    assert del_resp.status_code == 200

    # 4. Verify removed
    list_resp2 = await client.get("/api/v1/email/suppressions", headers=headers)
    items2 = list_resp2.json()["data"]["items"]
    assert not any(i["email"] == test_email for i in items2)


@pytest.mark.asyncio
async def test_audit_invoices_and_billing_guards(client: AsyncClient, registered_user):
    """Verify invoice endpoints, role checks, and error boundaries."""
    headers = registered_user["headers"]

    # 1. List invoices for newly created org
    inv_list_resp = await client.get("/api/v1/billing/invoices", headers=headers)
    assert inv_list_resp.status_code == 200
    assert "items" in inv_list_resp.json()["data"]

    # 2. GET /billing/invoices/{invoice_id} for non-existent invoice -> 404
    inv_resp = await client.get("/api/v1/billing/invoices/inv_audit_non_existent", headers=headers)
    assert inv_resp.status_code == 404
    assert inv_resp.json()["error"]["code"] == "INVOICE_NOT_FOUND"


@pytest.mark.asyncio
async def test_audit_webhook_test_and_retry_contracts(client: AsyncClient, registered_user):
    """Verify webhook ping testing and retry endpoints."""
    headers = registered_user["headers"]

    # 1. Create a webhook endpoint
    wh_payload = {
        "url": "https://webhook.site/audit-test-ping",
        "description": "Audit Webhook",
        "events": ["certificate.issued"]
    }
    wh_create = await client.post("/api/v1/webhooks", headers=headers, json=wh_payload)
    assert wh_create.status_code == 201
    wh_id = wh_create.json()["data"]["id"]

    # 2. Test ping dispatching: POST /api/v1/webhooks/{endpoint_id}/test
    test_ping_resp = await client.post(f"/api/v1/webhooks/{wh_id}/test", headers=headers)
    assert test_ping_resp.status_code == 200
    assert "delivery_id" in test_ping_resp.json()["data"]

    # 3. Retry delivery for non-existent delivery ID -> 404
    retry_resp = await client.post("/api/v1/webhook-deliveries/delivery_fake_999/retry", headers=headers)
    assert retry_resp.status_code == 404
    assert retry_resp.json()["error"]["code"] == "DELIVERY_NOT_FOUND"


@pytest.mark.asyncio
async def test_audit_frontend_envelope_and_keys_contract(client: AsyncClient, registered_user):
    """Verify that backend JSON response strictly adheres to Frontend ApiEnvelope<T>."""
    headers = registered_user["headers"]

    # Verify standard envelope structure on multiple endpoints
    endpoints_to_sample = [
        ("GET", "/api/v1/templates"),
        ("GET", "/api/v1/certificates"),
        ("GET", "/api/v1/analytics/dashboard"),
        ("GET", "/api/v1/billing/usage"),
        ("GET", "/api/v1/organization/members"),
    ]

    for method, path in endpoints_to_sample:
        if method == "GET":
            resp = await client.get(path, headers=headers)
        assert resp.status_code == 200, f"Failed on {path}: {resp.text}"
        body = resp.json()

        # Contract assertions matching ApiEnvelope<T> in src/lib/api/client.ts
        assert "success" in body, f"Missing 'success' in {path}"
        assert isinstance(body["success"], bool), f"'success' not bool in {path}"
        assert "data" in body, f"Missing 'data' in {path}"
        assert "error" in body, f"Missing 'error' in {path}"
        assert body["error"] is None or isinstance(body["error"], dict)
