import pytest
from datetime import datetime, timezone
from app.credentials.canonicalizer import canonicalize_json
from app.credentials.signers.ed25519_signer import Ed25519Signer
from app.credentials.serializers.open_badges import OpenBadgesV3Serializer
from app.credentials.serializers.w3c_vc import W3CVCSerializer
from app.services.credential_key_service import CredentialKeyService
from app.services.credential_signing_service import CredentialSigningService


class TestCanonicalizer:
    def test_canonicalize_deterministic_order(self):
        doc_a = {"b": 2, "a": 1, "nested": {"z": 10, "m": 5}}
        doc_b = {"a": 1, "nested": {"m": 5, "z": 10}, "b": 2}
        assert canonicalize_json(doc_a) == canonicalize_json(doc_b)

    def test_canonicalize_excludes_proof_block(self):
        doc_without_proof = {"id": "cred_123", "name": "Certificate"}
        doc_with_proof = {
            "id": "cred_123",
            "name": "Certificate",
            "proof": {"type": "Ed25519Signature2020", "proofValue": "xyz123"}
        }
        # Detached proof is excluded so the signed payload matches exactly
        assert canonicalize_json(doc_without_proof) == canonicalize_json(doc_with_proof)


class TestEd25519Signer:
    def test_generate_and_sign_and_verify(self):
        public_pem, enc_private = Ed25519Signer.generate_keypair()
        assert "BEGIN PUBLIC KEY" in public_pem
        assert enc_private is not None

        payload = b"test payload for verifiable credential"
        sig_b64 = Ed25519Signer.sign_bytes(payload, enc_private)
        assert isinstance(sig_b64, str)
        assert len(sig_b64) > 0

        # Verification succeeds with matching public key
        assert Ed25519Signer.verify_bytes(payload, sig_b64, public_pem) is True

        # Verification fails with altered payload
        assert Ed25519Signer.verify_bytes(payload + b"tampered", sig_b64, public_pem) is False

        # Verification fails with different key
        other_public_pem, _ = Ed25519Signer.generate_keypair()
        assert Ed25519Signer.verify_bytes(payload, sig_b64, other_public_pem) is False


class TestSerializers:
    def test_open_badges_v3_serializer(self):
        cred = {
            "credential_id": "cred_test_123",
            "recipient_name": "Alice Doe",
            "valid_from": datetime.now(timezone.utc),
            "certificate_number": "CERT-2026-001"
        }
        issuer = {
            "issuer_id": "iss_test_456",
            "name": "Tech Academy",
            "website": "https://academy.example.com",
            "email": "contact@academy.example.com"
        }
        achievement = {
            "achievement_id": "ach_test_789",
            "name": "Full Stack Engineer",
            "description": "Passed comprehensive assessment",
            "criteria": "Completed 10 projects and final exam",
            "skills": ["Python", "FastAPI", "React"]
        }

        doc = OpenBadgesV3Serializer.serialize(cred, issuer, achievement)
        assert "https://purl.imsglobal.org/spec/ob/v3.0/context.json" in doc["@context"]
        assert "OpenBadgeCredential" in doc["type"]
        assert doc["issuer"]["name"] == "Tech Academy"
        assert doc["credentialSubject"]["name"] == "Alice Doe"
        assert doc["credentialSubject"]["achievement"]["name"] == "Full Stack Engineer"
        assert "Python" in doc["credentialSubject"]["achievement"]["tag"]

    def test_w3c_vc_serializer(self):
        cred = {
            "credential_id": "cred_test_123",
            "recipient_name": "Bob Smith",
            "valid_from": datetime.now(timezone.utc),
            "certificate_number": "CERT-2026-002"
        }
        issuer = {
            "issuer_id": "iss_test_456",
            "name": "AI Institute",
            "website": "https://ai.example.com"
        }
        achievement = {
            "achievement_id": "ach_test_789",
            "name": "Machine Learning Specialist",
            "description": "Deep Learning certification",
            "skills": ["PyTorch", "TensorFlow"]
        }

        doc = W3CVCSerializer.serialize(cred, issuer, achievement)
        assert "https://www.w3.org/ns/credentials/v2" in doc["@context"]
        assert "VerifiableCredential" in doc["type"]
        assert doc["credentialSubject"]["name"] == "Bob Smith"
        assert doc["credentialSubject"]["hasCertification"]["name"] == "Machine Learning Specialist"
        assert "credentialStatus" in doc
