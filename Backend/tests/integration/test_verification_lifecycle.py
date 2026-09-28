import io
import pytest
from httpx import AsyncClient


async def create_published_template_and_certificate(client: AsyncClient, headers: dict) -> dict:
    # 1. Create template
    t_resp = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": "Trust & Verification Template"}
    )
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Publish template version
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200

    # 3. Generate certificate
    gen_payload = {
        "template_version_id": version_id,
        "data": {
            "recipient_name": "Atul Kumar",
            "recipient_email": "atul@example.com",
            "program_name": "AI Architecture Masterclass",
            "issue_date": "28 September 2026",
        }
    }
    gen_resp = await client.post("/api/v1/certificates/generate", headers=headers, json=gen_payload)
    assert gen_resp.status_code == 201
    return gen_resp.json()["data"]


@pytest.mark.asyncio
async def test_public_verification_and_privacy(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    code = cert["verification_code"]

    # Public verification (no auth headers!)
    resp = await client.get(f"/api/v1/public/verify/{code}")
    assert resp.status_code == 200
    data = resp.json()["data"]

    assert data["valid"] is True
    assert data["status"] == "valid"
    assert data["certificate"]["recipient_name"] == "Atul Kumar"
    assert data["certificate"]["certificate_number"] == cert["certificate_number"]
    assert data["certificate"]["program_name"] == "AI Architecture Masterclass"

    # PRIVACY TEST: Ensure private/internal fields are NEVER leaked
    json_str = resp.text
    assert "atul@example.com" not in json_str
    assert "pdf_key" not in json_str
    assert cert["id"] not in json_str


@pytest.mark.asyncio
async def test_full_revocation_and_restore_lifecycle(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    cert_id = cert["id"]
    code = cert["verification_code"]

    # 1. Initially valid
    v1 = await client.get(f"/api/v1/public/verify/{code}")
    assert v1.json()["data"]["valid"] is True

    # 2. Revoke certificate
    revoke_payload = {
        "reason": "Administrative error in recipient details",
        "notes": "Internal note: requested by admin"
    }
    rev_resp = await client.post(f"/api/v1/certificates/{cert_id}/revoke", headers=headers, json=revoke_payload)
    assert rev_resp.status_code == 200
    assert rev_resp.json()["data"]["status"] == "revoked"

    # 3. Public verification shows REVOKED immediately
    v2 = await client.get(f"/api/v1/public/verify/{code}")
    assert v2.status_code == 200
    data2 = v2.json()["data"]
    assert data2["valid"] is False
    assert data2["status"] == "revoked"
    assert data2["revocation_reason"] == "Administrative error in recipient details"

    # 4. Restore certificate
    res_resp = await client.post(f"/api/v1/certificates/{cert_id}/restore", headers=headers)
    assert res_resp.status_code == 200
    assert res_resp.json()["data"]["status"] == "generated"

    # 5. Public verification shows VALID again
    v3 = await client.get(f"/api/v1/public/verify/{code}")
    assert v3.status_code == 200
    assert v3.json()["data"]["valid"] is True
    assert v3.json()["data"]["status"] == "valid"


@pytest.mark.asyncio
async def test_bulk_revocation(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert1 = await create_published_template_and_certificate(client, headers)
    cert2 = await create_published_template_and_certificate(client, headers)

    bulk_payload = {
        "certificate_ids": [cert1["id"], cert2["id"]],
        "reason": "Batch re-issuance required",
    }
    resp = await client.post("/api/v1/certificates/bulk-revoke", headers=headers, json=bulk_payload)
    assert resp.status_code == 200
    assert resp.json()["data"]["revoked_count"] == 2

    # Both must now be revoked
    v1 = await client.get(f"/api/v1/public/verify/{cert1['verification_code']}")
    assert v1.json()["data"]["valid"] is False
    assert v1.json()["data"]["status"] == "revoked"

    v2 = await client.get(f"/api/v1/public/verify/{cert2['verification_code']}")
    assert v2.json()["data"]["valid"] is False
    assert v2.json()["data"]["status"] == "revoked"


@pytest.mark.asyncio
async def test_cryptographic_integrity_and_file_verification(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    cert_id = cert["id"]

    # 1. Internal integrity check
    integ_resp = await client.get(f"/api/v1/certificates/{cert_id}/integrity", headers=headers)
    assert integ_resp.status_code == 200
    integ_data = integ_resp.json()["data"]
    assert integ_data["valid"] is True
    assert integ_data["matched"] is True
    assert integ_data["stored_hash"] == integ_data["current_hash"]

    # 2. Download original PDF bytes
    pdf_resp = await client.get(f"/api/v1/certificates/{cert_id}/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    pdf_bytes = pdf_resp.content

    # 3. Public file verification with original PDF
    files = {"file": ("certificate.pdf", pdf_bytes, "application/pdf")}
    file_verify_resp = await client.post("/api/v1/public/verify-file", files=files)
    assert file_verify_resp.status_code == 200
    fv_data = file_verify_resp.json()["data"]
    assert fv_data["valid"] is True
    assert fv_data["integrity_matched"] is True
    assert fv_data["certificate"]["recipient_name"] == "Atul Kumar"

    # 4. Public file verification with altered/tampered PDF
    altered_bytes = pdf_bytes + b"\n%MALICIOUS_MODIFICATION"
    bad_files = {"file": ("tampered.pdf", altered_bytes, "application/pdf")}
    bad_verify_resp = await client.post("/api/v1/public/verify-file", files=bad_files)
    assert bad_verify_resp.status_code == 200
    bad_data = bad_verify_resp.json()["data"]
    assert bad_data["valid"] is False
    assert bad_data["integrity_matched"] is False


@pytest.mark.asyncio
async def test_certificate_timeline_and_events(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    cert_id = cert["id"]
    code = cert["verification_code"]

    # Trigger public scan
    await client.get(f"/api/v1/public/verify/{code}", headers={"User-Agent": "MobileScanner/1.0"})

    # Check verification events
    ev_resp = await client.get(f"/api/v1/certificates/{cert_id}/verification-events", headers=headers)
    assert ev_resp.status_code == 200
    events = ev_resp.json()["data"]
    assert len(events) >= 1
    assert events[0]["result"] == "valid"

    # Check certificate timeline
    timeline_resp = await client.get(f"/api/v1/certificates/{cert_id}/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    tl_data = timeline_resp.json()["data"]
    assert tl_data["certificate_id"] == cert_id
    assert len(tl_data["events"]) >= 2
    types = [e["type"] for e in tl_data["events"]]
    assert "generated" in types
    assert "verified_valid" in types


@pytest.mark.asyncio
async def test_public_certificate_download(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_published_template_and_certificate(client, headers)
    code = cert["verification_code"]

    # Download via public endpoint
    dl_resp = await client.get(f"/api/v1/public/certificates/{code}/download")
    assert dl_resp.status_code == 200
    assert "application/pdf" in dl_resp.headers["content-type"]
    assert len(dl_resp.content) > 1000
