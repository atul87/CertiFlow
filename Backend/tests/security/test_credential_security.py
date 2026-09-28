import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from app.credentials.signers.ed25519_signer import Ed25519Signer
from app.credentials.canonicalizer import canonicalize_json
from app.services.credential_signing_service import CredentialSigningService
from tests.integration.test_credentials_and_issuance import create_cert


@pytest.mark.asyncio
async def test_cryptographic_tamper_detection(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    # Issue valid credential
    res = await client.post("/api/v1/credentials", headers=headers, json={"certificate_id": cert_id})
    assert res.status_code == 201
    cred_id = res.json()["data"]["credential_id"]

    # Fetch original W3C VC document
    vc_res = await client.get(f"/api/v1/public/credentials/{cred_id}/vc")
    assert vc_res.status_code == 200
    original_vc = vc_res.json()

    # Verify original passes independent verification
    v_orig = await client.post("/api/v1/public/credentials/verify", json={"credential_payload": original_vc})
    assert v_orig.status_code == 200
    assert v_orig.json()["data"]["valid"] is True
    assert v_orig.json()["data"]["verification_status"] == "VALID"

    # TAMPER ATTACK 1: Alter recipient name
    tampered_vc = dict(original_vc)
    tampered_vc["credentialSubject"] = dict(original_vc["credentialSubject"])
    tampered_vc["credentialSubject"]["name"] = "Attacker Name"

    v_tampered = await client.post("/api/v1/public/credentials/verify", json={"credential_payload": tampered_vc})
    assert v_tampered.status_code == 200
    assert v_tampered.json()["data"]["valid"] is False
    assert v_tampered.json()["data"]["verification_status"] == "INVALID_SIGNATURE"

    # TAMPER ATTACK 2: Alter achievement name
    tampered_ach = dict(original_vc)
    tampered_ach["credentialSubject"] = dict(original_vc["credentialSubject"])
    subj_cert = dict(tampered_ach["credentialSubject"]["hasCertification"])
    subj_cert["name"] = "Honorary Doctorate in AI"
    tampered_ach["credentialSubject"]["hasCertification"] = subj_cert

    v_tampered2 = await client.post("/api/v1/public/credentials/verify", json={"credential_payload": tampered_ach})
    assert v_tampered2.status_code == 200
    assert v_tampered2.json()["data"]["valid"] is False
    assert v_tampered2.json()["data"]["verification_status"] == "INVALID_SIGNATURE"


@pytest.mark.asyncio
async def test_key_substitution_attack(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    res = await client.post("/api/v1/credentials", headers=headers, json={"certificate_id": cert_id})
    cred_id = res.json()["data"]["credential_id"]

    vc_res = await client.get(f"/api/v1/public/credentials/{cred_id}/vc")
    original_vc = vc_res.json()

    # Attacker generates their own rogue Ed25519 keypair
    rogue_public, rogue_private = Ed25519Signer.generate_keypair()

    # Attacker signs the VC payload with rogue key
    canonical_bytes = canonicalize_json(original_vc)
    rogue_signature = Ed25519Signer.sign_bytes(canonical_bytes, rogue_private)

    # Attacker substitutes the signature while claiming the legitimate issuer's verificationMethod
    substituted_vc = dict(original_vc)
    substituted_vc["proof"] = dict(original_vc["proof"])
    substituted_vc["proof"]["proofValue"] = rogue_signature

    v_sub = await client.post("/api/v1/public/credentials/verify", json={"credential_payload": substituted_vc})
    assert v_sub.status_code == 200
    assert v_sub.json()["data"]["valid"] is False
    assert v_sub.json()["data"]["verification_status"] == "INVALID_SIGNATURE"


@pytest.mark.asyncio
async def test_expired_credential_verification(client: AsyncClient, registered_user):
    headers = registered_user["headers"]
    cert = await create_cert(client, headers)
    cert_id = cert["id"]

    # Issue credential that expired yesterday
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)

    res = await client.post(
        "/api/v1/credentials",
        headers=headers,
        json={
            "certificate_id": cert_id,
            "valid_from": two_days_ago.isoformat(),
            "expires_at": yesterday.isoformat()
        }
    )
    assert res.status_code == 201
    cred_id = res.json()["data"]["credential_id"]

    # Verification endpoint must reject expired credential
    v_res = await client.get(f"/api/v1/public/credentials/{cred_id}/verify")
    assert v_res.status_code == 200
    assert v_res.json()["data"]["valid"] is False
    assert v_res.json()["data"]["verification_status"] == "EXPIRED"


@pytest.mark.asyncio
async def test_malformed_external_verification_payload(client: AsyncClient):
    # Missing proof
    res1 = await client.post(
        "/api/v1/public/credentials/verify",
        json={"credential_payload": {"@context": ["https://www.w3.org/ns/credentials/v2"], "type": ["VerifiableCredential"]}}
    )
    assert res1.status_code == 200
    assert res1.json()["data"]["verification_status"] == "MALFORMED"

    # Completely arbitrary dict
    res2 = await client.post(
        "/api/v1/public/credentials/verify",
        json={"credential_payload": {"random": "payload"}}
    )
    assert res2.status_code == 200
    assert res2.json()["data"]["verification_status"] == "MALFORMED"
