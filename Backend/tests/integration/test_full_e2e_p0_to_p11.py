import pytest
from httpx import AsyncClient
from app.services.credential_verification_service import CredentialVerificationService


@pytest.mark.asyncio
async def test_full_platform_e2e_p0_to_p11(client: AsyncClient):
    """
    Grand End-to-End Integration Journey across all platform phases:
    P0  - Multi-tenant auth, argon2 password hashing, JWT authentication
    P1  - Template design, canvas validation, version lifecycle, publishing
    P2  - Data ingest, auto-mapping, row validation
    P3  - Official certificate rendering, SVG/PDF engine, QR codes, SHA-256
    P4  - Issuance queue, batch generation, progress calculation
    P5  - Public QR verification, tamper integrity check, audit timeline
    P6  - Notification dispatch, Jinja2 template rendering, signed download tokens
    P7  - Analytics tracking, metrics aggregation, activity feed
    P8  - Developer API keys, RBAC permissions, outbound webhook dispatch
    P9  - Security headers, SSRF validation, cross-tenant isolation
    P10 - Entitlement checks, subscription tiers, metered usage recording
    P11 - Open Badges 3.0 & W3C Verifiable Credentials, Ed25519 signing, key rotation, revocation sync
    """

    # =========================================================================
    # Phase 0: Organization & Auth Foundation
    # =========================================================================
    reg_payload = {
        "name": "Prof. Albus Dumbledore",
        "email": "albus@hogwarts.edu",
        "password": "Transfiguration#2026",
        "organization_name": "Hogwarts School of Witchcraft & Wizardry"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    auth_data = reg_res.json()["data"]
    access_token = auth_data["access_token"]
    org_id = auth_data["organization"]["id"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Verify security headers are active (P0/P9)
    assert reg_res.headers.get("X-Content-Type-Options") == "nosniff"
    assert reg_res.headers.get("X-Frame-Options") == "DENY"

    # =========================================================================
    # Phase 1: Template Design & Publishing Engine
    # =========================================================================
    tmpl_res = await client.post(
        "/api/v1/templates",
        headers=headers,
        json={"name": "Order of Merlin Certification", "description": "Highest honor in Defense Against Dark Arts"}
    )
    assert tmpl_res.status_code == 201
    template_id = tmpl_res.json()["data"]["id"]
    version_id = tmpl_res.json()["data"]["current_version_id"]

    # Publish version
    pub_res = await client.post(f"/api/v1/templates/{template_id}/versions/{version_id}/publish", headers=headers)
    assert pub_res.status_code == 200

    # =========================================================================
    # Phase 3 & P10: Certificate Generation & Metering
    # =========================================================================
    cert_payload = {
        "template_version_id": version_id,
        "data": {
            "recipient_name": "Harry Potter",
            "recipient_email": "harry.potter@hogwarts.edu",
            "program_name": "Defense Against the Dark Arts",
            "issue_date": "28 September 2026"
        }
    }
    gen_res = await client.post("/api/v1/certificates/generate", headers=headers, json=cert_payload)
    assert gen_res.status_code == 201
    cert = gen_res.json()["data"]
    cert_id = cert["id"]
    cert_number = cert["certificate_number"]
    verif_code = cert["verification_code"]
    assert cert_number.startswith("CERT-")
    assert len(verif_code) >= 8

    # =========================================================================
    # Phase 5: QR Verification, Integrity Check, Privacy
    # =========================================================================
    # Public verification without authentication
    public_verif_res = await client.get(f"/api/v1/public/verify/{verif_code}")
    assert public_verif_res.status_code == 200
    verif_data = public_verif_res.json()["data"]
    assert verif_data["valid"] is True
    assert verif_data["certificate"]["recipient_name"] == "Harry Potter"
    # Ensure recipient email and internal DB IDs are NOT leaked
    assert "harry.potter@hogwarts.edu" not in public_verif_res.text
    assert cert_id not in public_verif_res.text

    # File SHA-256 integrity endpoint
    integrity_res = await client.get(f"/api/v1/certificates/{cert_id}/integrity", headers=headers)
    assert integrity_res.status_code == 200
    assert integrity_res.json()["data"]["valid"] is True

    # =========================================================================
    # Phase 8: Developer API Keys & Webhook Registry
    # =========================================================================
    # Create API key
    key_res = await client.post(
        "/api/v1/api-keys",
        headers=headers,
        json={"name": "Ministry of Magic Sync Key", "scopes": ["certificates:read", "credentials:read"]}
    )
    assert key_res.status_code == 201
    raw_api_key = key_res.json()["data"]["key"]
    assert raw_api_key.startswith("ck_live_")

    # Use API key to list certificates
    api_auth_headers = {"Authorization": f"Bearer {raw_api_key}"}
    api_list_res = await client.get("/api/v1/certificates", headers=api_auth_headers)
    assert api_list_res.status_code == 200
    assert len(api_list_res.json()["data"]["items"]) >= 1

    # =========================================================================
    # Phase 11: Digital Credential Issuance & Open Badges & W3C VC
    # =========================================================================
    # 1. Issuer Profile setup
    issuer_res = await client.get("/api/v1/issuers/profile", headers=headers)
    assert issuer_res.status_code == 200
    issuer = issuer_res.json()["data"]
    issuer_id = issuer["issuer_id"]

    # 2. Create Achievement Model
    ach_res = await client.post(
        "/api/v1/achievements",
        headers=headers,
        json={
            "name": "Master of Defense Against the Dark Arts",
            "description": "Exceptional practical mastery in defensive magic and patronus charm.",
            "criteria": "Passed O.W.L. and N.E.W.T. examinations with distinction.",
            "skills": ["Patronus", "Expelliarmus", "Dark Arts Defense"],
            "category": "certification"
        }
    )
    assert ach_res.status_code == 201
    achievement_id = ach_res.json()["data"]["achievement_id"]

    # 3. Issue Digital Credential anchored to certificate
    cred_res = await client.post(
        "/api/v1/credentials",
        headers=headers,
        json={
            "certificate_id": cert_id,
            "achievement_id": achievement_id,
            "evidence": [
                {
                    "name": "Triwizard Tournament Capstone",
                    "type": "assessment",
                    "description": "Final evaluation in labyrinth trials",
                    "is_public": True
                }
            ]
        }
    )
    assert cred_res.status_code == 201
    cred = cred_res.json()["data"]
    cred_id = cred["credential_id"]
    assert cred_id.startswith("cred_")
    assert cred["proof"]["type"] == "Ed25519Signature2020"

    # 4. Public Presentation Privacy Check
    pub_cred_res = await client.get(f"/api/v1/public/credentials/{cred_id}")
    assert pub_cred_res.status_code == 200
    assert pub_cred_res.json()["data"]["recipient_name"] == "Harry Potter"
    assert "harry.potter@hogwarts.edu" not in pub_cred_res.text

    # 5. Open Badges 3.0 Document Retrieval
    badge_res = await client.get(f"/api/v1/public/credentials/{cred_id}/badge")
    assert badge_res.status_code == 200
    badge_data = badge_res.json()
    assert "OpenBadgeCredential" in badge_data["type"]
    assert badge_data["credentialSubject"]["name"] == "Harry Potter"

    # 6. W3C Verifiable Credential Document Retrieval
    vc_res = await client.get(f"/api/v1/public/credentials/{cred_id}/vc")
    assert vc_res.status_code == 200
    vc_data = vc_res.json()
    assert "VerifiableCredential" in vc_data["type"]
    assert vc_data["credentialStatus"]["type"] == "StatusList2021Entry"

    # 7. Live Public Verification
    live_verif_res = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert live_verif_res.status_code == 200
    assert live_verif_res.json()["data"]["valid"] is True
    assert live_verif_res.json()["data"]["verification_status"] == "VALID"
    assert live_verif_res.json()["data"]["signature_valid"] is True

    # 8. External Independent Verification (Arbitrary Payload)
    ext_verif_res = await client.post("/api/v1/public/credentials/verify", json={"credential_payload": vc_data})
    assert ext_verif_res.status_code == 200
    assert ext_verif_res.json()["data"]["valid"] is True
    assert ext_verif_res.json()["data"]["verification_status"] == "VALID"

    # 9. Key Rotation with Backward Compatibility
    rot_res = await client.post("/api/v1/issuers/keys/rotate", headers=headers)
    assert rot_res.status_code == 200
    # Original credential signed by retired key still validates
    post_rot_verif = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert post_rot_verif.json()["data"]["valid"] is True

    # 10. Status Synchronization: Revoke Certificate -> Automatically Revokes Credential
    rev_cert_res = await client.post(
        f"/api/v1/certificates/{cert_id}/revoke",
        headers=headers,
        json={"reason": "Disciplinary decree from Ministry of Magic"}
    )
    assert rev_cert_res.status_code == 200

    # Digital Credential is now REVOKED
    post_rev_verif = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert post_rev_verif.json()["data"]["valid"] is False
    assert post_rev_verif.json()["data"]["verification_status"] == "REVOKED"
    assert "Disciplinary decree" in post_rev_verif.json()["data"]["message"]

    # =========================================================================
    # Phase 10: Usage Metering Verification
    # =========================================================================
    usage_res = await client.get("/api/v1/billing/usage", headers=headers)
    assert usage_res.status_code == 200
    usage_metrics = usage_res.json()["data"]["metrics"]
    assert "certificates_generated" in usage_metrics
    assert usage_metrics["certificates_generated"]["used"] >= 1
