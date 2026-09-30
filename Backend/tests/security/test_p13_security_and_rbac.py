"""
P13.4 Security Hardening & RBAC Validation Test Suite.
Validates:
1. Tenant isolation across templates, certificates, verification events, timelines, imports, and jobs.
2. Fine-grained RBAC role enforcement (Owner vs Admin vs Member vs Viewer).
3. Webhook SSRF defense blocking loopback, cloud metadata (169.254.169.254), and private networks.
4. Input validation and malicious upload protection.
"""
import pytest
from httpx import AsyncClient
from bson import ObjectId
from datetime import datetime, timezone

from app.core.database import DatabaseManager
from app.repositories.template_repository import TemplateRepository
from app.repositories.template_version_repository import TemplateVersionRepository
from app.repositories.certificate_repository import CertificateRepository
from app.security.webhooks import WebhookSecurity
from app.core.exceptions import ValidationError


@pytest.mark.asyncio
async def test_p13_cross_tenant_idor_protection(client: AsyncClient):
    """
    Ensure complete tenant isolation across certificates, PDF downloads,
    timelines, verification events, and imports.
    """
    # 1. Register Tenant A
    res_a = await client.post("/api/v1/auth/register", json={
        "name": "Tenant Alpha Admin",
        "email": "admin@tenant-alpha.io",
        "password": "AlphaPassword123!"
    })
    assert res_a.status_code == 201
    auth_a = {"Authorization": f"Bearer {res_a.json()['data']['access_token']}"}
    org_id_a = res_a.json()["data"]["organization"]["id"]
    user_id_a = res_a.json()["data"]["user"]["id"]

    # 2. Register Tenant B
    res_b = await client.post("/api/v1/auth/register", json={
        "name": "Tenant Beta Attacker",
        "email": "attacker@tenant-beta.io",
        "password": "BetaPassword123!"
    })
    assert res_b.status_code == 201
    auth_b = {"Authorization": f"Bearer {res_b.json()['data']['access_token']}"}
    org_id_b = res_b.json()["data"]["organization"]["id"]

    # 3. Tenant A creates and publishes a template
    tmpl = await TemplateRepository.create(
        organization_id=org_id_a,
        name="Confidential Executive Cert",
        created_by=user_id_a,
    )
    tmpl_id_a = tmpl["id"]

    v_doc = await TemplateVersionRepository.create_version(
        template_id=tmpl_id_a,
        organization_id=org_id_a,
        created_by=user_id_a,
        status="published"
    )
    v_id_a = v_doc["id"]

    # 4. Tenant A creates a certificate
    cert = await CertificateRepository.create(
        organization_id=org_id_a,
        template_id=tmpl_id_a,
        template_version_id=v_id_a,
        certificate_number="ALPHA-CONF-001",
        verification_code="A1B2C3D4E5F6",
        recipient={"name": "Alice Officer", "email": "alice@tenant-alpha.io"},
        data={"title": "Chief Executive"},
        template_snapshot={},
        created_by=user_id_a,
    )
    cert_id_a = cert["id"]
    await CertificateRepository.update_status(
        cert_id=cert_id_a,
        status="generated",
        file_info={"pdf_key": "certs/alpha/cert.pdf", "sha256": "fakehash", "size_bytes": 1024},
    )

    # 5. Tenant B attempts IDOR on Tenant A's certificate
    res = await client.get(f"/api/v1/certificates/{cert_id_a}", headers=auth_b)
    assert res.status_code == 404

    # 6. Tenant B attempts to download Tenant A's certificate PDF
    res = await client.get(f"/api/v1/certificates/{cert_id_a}/pdf", headers=auth_b)
    assert res.status_code == 404

    # 7. Tenant B attempts to read Tenant A's certificate timeline
    res = await client.get(f"/api/v1/certificates/{cert_id_a}/timeline", headers=auth_b)
    assert res.status_code == 404

    # 8. Tenant B attempts to read Tenant A's verification scan history
    res = await client.get(f"/api/v1/certificates/{cert_id_a}/verification-events", headers=auth_b)
    assert res.status_code == 404

    # 9. Tenant B attempts to revoke Tenant A's certificate
    res = await client.post(f"/api/v1/certificates/{cert_id_a}/revoke", headers=auth_b, json={"reason": "Hacked"})
    assert res.status_code == 404

    # 10. Tenant B attempts to upload import using Tenant A's template ID
    csv_bytes = b"recipient_name,recipient_email\nJohn Doe,john@test.com"
    files = {"file": ("test.csv", csv_bytes, "text/csv")}
    data = {"template_id": tmpl_id_a}
    res = await client.post("/api/v1/imports", headers=auth_b, data=data, files=files)
    assert res.status_code in (404, 400)


@pytest.mark.asyncio
async def test_p13_rbac_viewer_restrictions(client: AsyncClient):
    """
    Validate that an organization member with 'viewer' role can inspect resources
    but is strictly forbidden from creating, mutating, or revoking them.
    """
    # 1. Register Org Owner
    res_owner = await client.post("/api/v1/auth/register", json={
        "name": "Org Boss",
        "email": "boss@rbac-test.io",
        "password": "Password123!"
    })
    assert res_owner.status_code == 201
    org_id = res_owner.json()["data"]["organization"]["id"]
    owner_auth = {"Authorization": f"Bearer {res_owner.json()['data']['access_token']}"}

    # 2. Register Viewer User
    res_viewer = await client.post("/api/v1/auth/register", json={
        "name": "Observer Jane",
        "email": "jane@rbac-test.io",
        "password": "Password123!"
    })
    assert res_viewer.status_code == 201
    viewer_user_id = res_viewer.json()["data"]["user"]["id"]

    # 3. Add Viewer as 'viewer' role in the Owner's organization
    members_coll = DatabaseManager.get_collection("organization_members")
    await members_coll.insert_one({
        "organization_id": ObjectId(org_id),
        "user_id": ObjectId(viewer_user_id),
        "role": "viewer",
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    })

    # Switch Viewer's active session to Owner's org
    switch_res = await client.post(
        "/api/v1/organizations/switch",
        json={"organization_id": org_id},
        headers={"Authorization": f"Bearer {res_viewer.json()['data']['access_token']}"}
    )
    assert switch_res.status_code == 200
    viewer_auth = {"Authorization": f"Bearer {switch_res.json()['data']['access_token']}"}

    # 4. Viewer CAN list certificates
    list_res = await client.get("/api/v1/certificates", headers=viewer_auth)
    assert list_res.status_code == 200

    # 5. Viewer CANNOT generate certificate
    gen_res = await client.post("/api/v1/certificates/generate", headers=viewer_auth, json={
        "template_id": str(ObjectId()),
        "recipient": {"name": "Test", "email": "test@test.com"},
        "data": {}
    })
    assert gen_res.status_code == 403
    assert gen_res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

    # 6. Viewer CANNOT create imports
    csv_bytes = b"name,email\nTest,test@test.com"
    imp_res = await client.post(
        "/api/v1/imports",
        headers=viewer_auth,
        data={"template_id": str(ObjectId())},
        files={"file": ("test.csv", csv_bytes, "text/csv")}
    )
    assert imp_res.status_code == 403
    assert imp_res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"

    # 7. Viewer CANNOT create issuance jobs
    job_res = await client.post("/api/v1/issuance-jobs", headers=viewer_auth, json={
        "import_id": str(ObjectId()),
        "template_version_id": str(ObjectId())
    })
    assert job_res.status_code == 403
    assert job_res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


@pytest.mark.asyncio
async def test_p13_ssrf_webhook_blocking():
    """
    Verify SSRF defense engine blocks loopback, private IPv4, and AWS metadata addresses.
    """
    # 1. AWS Cloud Metadata IP
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://169.254.169.254/latest/meta-data/")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # 2. Localhost IPv4 loopback
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://127.0.0.1:8000/internal-metrics")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # 3. Private 10.0.0.0/8 network
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://10.1.2.3/notify")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # 4. Private 192.168.0.0/16 network
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("http://192.168.1.1/webhook")
    assert exc.value.code == "WEBHOOK_SSRF_BLOCKED"

    # 5. Non-HTTP protocols (e.g. file://, gopher://)
    with pytest.raises(ValidationError) as exc:
        WebhookSecurity.validate_destination_url("file:///etc/passwd")
    assert exc.value.code == "INVALID_WEBHOOK_SCHEME"

    # 6. Valid public HTTPS URL
    valid_url = WebhookSecurity.validate_destination_url("https://hooks.slack.com/services/T00/B00/X00")
    assert valid_url == "https://hooks.slack.com/services/T00/B00/X00"


@pytest.mark.asyncio
async def test_p13_rate_limiting_sliding_window():
    """
    Validate RateLimiter sliding window and threshold exhaustion.
    """
    from app.services.rate_limiter import RateLimiter
    unique_key = f"test_rate_limit_{ObjectId()}"

    # Fire 5 allowed requests
    for i in range(5):
        allowed = await RateLimiter.is_allowed(unique_key, max_requests=5, window_seconds=60, fail_closed=True)
        assert allowed is True, f"Request {i+1} should have been allowed"

    # 6th request must be rejected (exhausted)
    exhausted = await RateLimiter.is_allowed(unique_key, max_requests=5, window_seconds=60, fail_closed=True)
    assert exhausted is False, "6th request must be blocked by rate limit"
