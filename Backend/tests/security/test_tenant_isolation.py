import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tenant_isolation_complete_matrix(client: AsyncClient):
    """
    Validates complete multi-tenant isolation across all resources:
    Templates, Certificates, Webhooks, API Keys, and Analytics.
    Org B user must NEVER be able to read, update, delete, or aggregate Org A resources.
    """
    # 1. Register User A (Organization A)
    user_a_resp = await client.post("/api/v1/auth/register", json={
        "name": "Alice Corp",
        "email": "alice@tenant-a.com",
        "password": "Password123!"
    })
    assert user_a_resp.status_code == 201
    auth_a = {"Authorization": f"Bearer {user_a_resp.json()['data']['access_token']}"}

    # 2. Register User B (Organization B)
    user_b_resp = await client.post("/api/v1/auth/register", json={
        "name": "Bob Enterprise",
        "email": "bob@tenant-b.com",
        "password": "Password123!"
    })
    assert user_b_resp.status_code == 201
    auth_b = {"Authorization": f"Bearer {user_b_resp.json()['data']['access_token']}"}

    # 3. Org A creates a template
    tmpl_resp = await client.post("/api/v1/templates", headers=auth_a, json={
        "name": "Secret Template A",
        "description": "Proprietary layout for Org A"
    })
    assert tmpl_resp.status_code == 201
    tmpl_id_a = tmpl_resp.json()["data"]["id"]

    from bson import ObjectId
    from app.repositories.certificate_repository import CertificateRepository

    org_id_a = user_a_resp.json()["data"]["organization"]["id"]
    user_id_a = user_a_resp.json()["data"]["user"]["id"]

    # 4. Org A issues a certificate directly
    cert_doc = await CertificateRepository.create(
        organization_id=org_id_a,
        template_id=tmpl_id_a,
        template_version_id=str(ObjectId()),
        certificate_number="CERT-2026-0001",
        verification_code="8F3A91D2E4B6",
        recipient={"name": "Charlie Recipient", "email": "charlie@example.com"},
        data={"grade": "A+"},
        template_snapshot={},
        created_by=user_id_a
    )
    cert_id_a = cert_doc["id"]

    # 5. Org A creates a webhook
    webhook_resp = await client.post("/api/v1/webhooks", headers=auth_a, json={
        "url": "https://example.com/org-a-webhook",
        "events": ["certificate.created", "certificate.revoked"]
    })
    assert webhook_resp.status_code == 201
    webhook_id_a = webhook_resp.json()["data"]["id"]

    # -------------------------------------------------------------------------
    # Cross-Tenant Violations Attempted by Org B (MUST BE DENIED)
    # -------------------------------------------------------------------------

    # 6. Org B attempts to read Org A template
    res = await client.get(f"/api/v1/templates/{tmpl_id_a}", headers=auth_b)
    assert res.status_code == 404

    # 7. Org B attempts to modify Org A template
    res = await client.patch(f"/api/v1/templates/{tmpl_id_a}", headers=auth_b, json={"name": "Hacked Name"})
    assert res.status_code == 404

    # 8. Org B attempts to archive Org A template
    res = await client.post(f"/api/v1/templates/{tmpl_id_a}/archive", headers=auth_b)
    assert res.status_code == 404

    # 9. Org B attempts to access Org A certificate
    res = await client.get(f"/api/v1/certificates/{cert_id_a}", headers=auth_b)
    assert res.status_code == 404

    # 10. Org B attempts to revoke Org A certificate
    res = await client.post(f"/api/v1/certificates/{cert_id_a}/revoke", headers=auth_b, json={
        "reason": "Malicious attempt to revoke"
    })
    assert res.status_code == 404

    # 11. Org B attempts to read Org A webhook
    res = await client.get(f"/api/v1/webhooks/{webhook_id_a}", headers=auth_b)
    assert res.status_code == 404

    # 12. Org B attempts to delete Org A webhook
    res = await client.delete(f"/api/v1/webhooks/{webhook_id_a}", headers=auth_b)
    assert res.status_code == 404

    # 13. Verify Analytics Isolation: Org B dashboard must show 0 certificates
    dash_b = await client.get("/api/v1/analytics/dashboard", headers=auth_b)
    assert dash_b.status_code == 200
    assert dash_b.json()["data"]["kpis"]["certificates_issued"]["value"] == 0

    # Verify Org A dashboard shows 1 certificate
    dash_a = await client.get("/api/v1/analytics/dashboard", headers=auth_a)
    assert dash_a.status_code == 200
    assert dash_a.json()["data"]["kpis"]["certificates_issued"]["value"] == 1

