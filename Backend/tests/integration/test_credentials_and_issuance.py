import pytest
from httpx import AsyncClient


async def create_cert(client: AsyncClient, headers: dict) -> dict:
    # 1. Create template
    t_resp = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": "P11 Credential Standard Template"}
    )
    assert t_resp.status_code == 201
    template_id = t_resp.json()["data"]["id"]
    version_id = t_resp.json()["data"]["current_version_id"]

    # 2. Publish version
    pub_resp = await client.post(
        f"/api/v1/templates/{template_id}/versions/{version_id}/publish",
        headers=headers,
    )
    assert pub_resp.status_code == 200

    # 3. Generate certificate
    gen_payload = {
        "template_version_id": version_id,
        "data": {
            "recipient_name": "Devin Spider",
            "recipient_email": "devin.spider@example.com",
            "program_name": "Verifiable Credentials & Open Badges",
            "issue_date": "28 September 2026",
        }
    }
    gen_resp = await client.post("/api/v1/certificates/generate", headers=headers, json=gen_payload)
    assert gen_resp.status_code == 201
    return gen_resp.json()["data"]


@pytest.mark.asyncio
async def test_issuer_profile_and_key_rotation(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # 1. Get default issuer profile
    res = await client.get("/api/v1/issuers/profile", headers=headers)
    assert res.status_code == 200
    issuer = res.json()["data"]
    assert issuer["issuer_id"].startswith("iss_")
    assert issuer["active_key_id"].startswith("key_")
    issuer_id = issuer["issuer_id"]

    # 2. Update issuer profile
    up_res = await client.put(
        "/api/v1/issuers/profile",
        headers=headers,
        json={
            "name": "Global Standards Institute",
            "website": "https://gsi.example.org",
            "email": "credentials@gsi.example.org"
        }
    )
    assert up_res.status_code == 200
    assert up_res.json()["data"]["name"] == "Global Standards Institute"

    # 3. Rotate keys
    rot_res = await client.post("/api/v1/issuers/keys/rotate", headers=headers)
    assert rot_res.status_code == 200
    assert rot_res.json()["data"]["algorithm"] == "Ed25519"

    # 4. Public resolution
    pub_res = await client.get(f"/api/v1/public/issuers/{issuer_id}")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()["data"]
    assert pub_data["name"] == "Global Standards Institute"
    assert len(pub_data["public_keys"]) >= 2
    # Verify no private keys leaked
    assert "private" not in pub_res.text.lower()


@pytest.mark.asyncio
async def test_achievement_crud(client: AsyncClient, registered_user):
    headers = registered_user["headers"]

    # Create achievement
    payload = {
        "name": "Machine Learning Engineer",
        "description": "Demonstrated mastery of deep neural networks and NLP models.",
        "criteria": "Completed 120 hours coursework and final capstone evaluation.",
        "skills": ["PyTorch", "Transformers", "Python"],
        "category": "certification"
    }
    create_res = await client.post("/api/v1/achievements", headers=headers, json=payload)
    assert create_res.status_code == 201
    ach = create_res.json()["data"]
    assert ach["achievement_id"].startswith("ach_")
    ach_id = ach["achievement_id"]

    # List achievements
    list_res = await client.get("/api/v1/achievements", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["data"]["total"] >= 1

    # Update achievement
    up_res = await client.put(
        f"/api/v1/achievements/{ach_id}",
        headers=headers,
        json={"level": "advanced"}
    )
    assert up_res.status_code == 200
    assert up_res.json()["data"]["level"] == "advanced"

    # Delete achievement
    del_res = await client.delete(f"/api/v1/achievements/{ach_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_credential_issuance_standards_and_verification(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    # 1. Issue Digital Credential anchored to certificate
    issue_payload = {
        "certificate_id": cert_id,
        "evidence": [
            {
                "name": "Capstone Repository",
                "type": "project",
                "description": "GitHub repository with passing CI test suite",
                "url": "https://github.com/example/capstone",
                "is_public": True
            }
        ]
    }
    issue_res = await client.post("/api/v1/credentials", headers=headers, json=issue_payload)
    assert issue_res.status_code == 201
    cred = issue_res.json()["data"]
    assert cred["credential_id"].startswith("cred_")
    assert cred["signature_algorithm"] == "Ed25519"
    assert cred["proof"] is not None
    assert cred["proof"]["type"] == "Ed25519Signature2020"
    cred_id = cred["credential_id"]

    # 2. Public Credential Presentation (Privacy Test)
    pub_res = await client.get(f"/api/v1/public/credentials/{cred_id}")
    assert pub_res.status_code == 200
    pub_cred = pub_res.json()["data"]
    assert pub_cred["recipient_name"] == "Devin Spider"
    assert pub_cred["status"] == "active"
    # PRIVACY ASSERTS: email and DB ids MUST NOT be present
    assert "devin.spider@example.com" not in pub_res.text
    assert cert_id not in pub_res.text

    # 3. Open Badges 3.0 Document Endpoint
    badge_res = await client.get(f"/api/v1/public/credentials/{cred_id}/badge")
    assert badge_res.status_code == 200
    badge_json = badge_res.json()
    assert "OpenBadgeCredential" in badge_json["type"]
    assert "https://purl.imsglobal.org/spec/ob/v3.0/context.json" in badge_json["@context"]
    assert badge_json["credentialSubject"]["name"] == "Devin Spider"
    assert len(badge_json["evidence"]) == 1

    # 4. W3C Verifiable Credential Document Endpoint
    vc_res = await client.get(f"/api/v1/public/credentials/{cred_id}/vc")
    assert vc_res.status_code == 200
    vc_json = vc_res.json()
    assert "VerifiableCredential" in vc_json["type"]
    assert "credentialStatus" in vc_json
    assert vc_json["credentialSubject"]["name"] == "Devin Spider"

    # 5. Live Cryptographic Verification Endpoint
    verify_res = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert verify_res.status_code == 200
    v_data = verify_res.json()["data"]
    assert v_data["valid"] is True
    assert v_data["verification_status"] == "VALID"
    assert v_data["signature_valid"] is True
    assert v_data["status_valid"] is True


@pytest.mark.asyncio
async def test_credential_lifecycle_and_certificate_revocation_sync(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    # Issue digital credential
    issue_res = await client.post("/api/v1/credentials", headers=headers, json={"certificate_id": cert_id})
    assert issue_res.status_code == 201
    cred_id = issue_res.json()["data"]["credential_id"]

    # Initial verification: VALID
    v1 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v1.json()["data"]["valid"] is True
    assert v1.json()["data"]["verification_status"] == "VALID"

    # Suspend credential
    susp_res = await client.post(
        f"/api/v1/credentials/{cred_id}/suspend",
        headers=headers,
        json={"reason": "Audit review under investigation"}
    )
    assert susp_res.status_code == 200
    assert susp_res.json()["data"]["status"] == "suspended"

    # Verification: SUSPENDED
    v2 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v2.json()["data"]["valid"] is False
    assert v2.json()["data"]["verification_status"] == "SUSPENDED"

    # Restore credential
    rest_res = await client.post(f"/api/v1/credentials/{cred_id}/restore", headers=headers)
    assert rest_res.status_code == 200
    assert rest_res.json()["data"]["status"] == "active"

    # Verification: VALID again
    v3 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v3.json()["data"]["valid"] is True
    assert v3.json()["data"]["verification_status"] == "VALID"

    # Revoke certificate — digital credential must automatically sync to REVOKED!
    revoke_cert_res = await client.post(
        f"/api/v1/certificates/{cert_id}/revoke",
        headers=headers,
        json={"reason": "Plagiarism identified in final capstone"}
    )
    assert revoke_cert_res.status_code == 200

    # Verification of credential: must be REVOKED
    v4 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v4.json()["data"]["valid"] is False
    assert v4.json()["data"]["verification_status"] == "REVOKED"
    assert "Plagiarism identified" in v4.json()["data"]["message"]


@pytest.mark.asyncio
async def test_key_rotation_preserves_verification_history(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    # Issue credential under Key 1
    issue_res = await client.post("/api/v1/credentials", headers=headers, json={"certificate_id": cert_id})
    cred_id = issue_res.json()["data"]["credential_id"]

    # Verify under Key 1
    v1 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v1.json()["data"]["valid"] is True

    # Rotate keys (Key 1 retired, Key 2 active)
    rot_res = await client.post("/api/v1/issuers/keys/rotate", headers=headers)
    assert rot_res.status_code == 200

    # Credential signed by retired Key 1 MUST still verify as VALID
    v2 = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v2.json()["data"]["valid"] is True
    assert v2.json()["data"]["verification_status"] == "VALID"
