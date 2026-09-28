from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.repositories.credential_repository import CredentialRepository
from app.repositories.issuer_repository import IssuerRepository
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.credential_key_repository import CredentialKeyRepository
from app.repositories.credential_event_repository import CredentialEventRepository
from app.services.credential_signing_service import CredentialSigningService
from app.credentials.serializers.w3c_vc import W3CVCSerializer
from app.schemas.credential import CredentialVerificationResponse

logger = logging.getLogger(__name__)


class CredentialVerificationService:
    @classmethod
    async def verify_by_credential_id(cls, credential_id: str) -> Dict[str, Any]:
        """
        Comprehensive verification pipeline for CertiFlow credentials:
        1. Credential existence
        2. Revocation & Suspension check
        3. Expiration validation
        4. Issuer & Key resolution
        5. Cryptographic signature validation
        """
        cred = await CredentialRepository.get_by_credential_id(credential_id)
        if not cred:
            return {
                "valid": False,
                "verification_status": "NOT_FOUND",
                "credential_id": credential_id,
                "message": f"Credential '{credential_id}' not found in registry."
            }

        now = datetime.now(timezone.utc)
        current_status = cred.get("status", "active").lower()

        # Check status: Revoked
        if current_status == "revoked":
            return {
                "valid": False,
                "verification_status": "REVOKED",
                "credential_id": credential_id,
                "recipient_name": cred.get("recipient_name"),
                "issued_at": cred.get("valid_from"),
                "message": f"Credential was REVOKED. Reason: {cred.get('revocation_reason', 'Unspecified')}"
            }

        # Check status: Suspended
        if current_status == "suspended":
            return {
                "valid": False,
                "verification_status": "SUSPENDED",
                "credential_id": credential_id,
                "recipient_name": cred.get("recipient_name"),
                "message": "Credential is currently SUSPENDED."
            }

        # Check expiration
        expires_at = cred.get("expires_at")
        if expires_at:
            if isinstance(expires_at, str):
                try:
                    expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                except Exception:
                    pass
            if isinstance(expires_at, datetime):
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at < now:
                    return {
                        "valid": False,
                        "verification_status": "EXPIRED",
                        "credential_id": credential_id,
                        "recipient_name": cred.get("recipient_name"),
                        "expires_at": expires_at,
                        "message": "Credential has EXPIRED."
                    }

        # Resolve Issuer
        issuer = await IssuerRepository.get_by_issuer_id(cred["issuer_id"])
        if not issuer:
            return {
                "valid": False,
                "verification_status": "UNKNOWN_ISSUER",
                "credential_id": credential_id,
                "message": f"Issuer '{cred['issuer_id']}' could not be resolved."
            }

        # Resolve Achievement
        achievement = await AchievementRepository.get_by_id(cred["achievement_id"])
        if not achievement:
            achievement = {
                "name": "Achievement",
                "description": "",
                "criteria": "",
                "skills": []
            }

        # Resolve Key
        key_id = cred.get("key_id", "default_key")
        key_doc = await CredentialKeyRepository.get_key_by_id(cred["issuer_id"], key_id)
        if not key_doc:
            return {
                "valid": False,
                "verification_status": "UNKNOWN_KEY",
                "credential_id": credential_id,
                "message": f"Signing key '{key_id}' for issuer is not found."
            }

        # Reconstruct canonical signed payload
        full_doc = W3CVCSerializer.serialize(
            credential=cred,
            issuer=issuer,
            achievement=achievement,
            evidence_items=cred.get("evidence"),
            proof=cred.get("proof")
        )

        sig_valid = CredentialSigningService.verify_payload_signature(full_doc, key_doc["public_key"])
        if not sig_valid:
            return {
                "valid": False,
                "verification_status": "INVALID_SIGNATURE",
                "credential_id": credential_id,
                "recipient_name": cred.get("recipient_name"),
                "message": "Cryptographic signature verification FAILED. Credential may have been tampered with."
            }

        # Record verification event
        await CredentialEventRepository.record_event(
            credential_id=credential_id,
            event_type="credential.verified",
            organization_id=cred.get("organization_id"),
            metadata={"status": "VALID", "verified_at": now.isoformat()}
        )

        return {
            "valid": True,
            "verification_status": "VALID",
            "credential_id": credential_id,
            "recipient_name": cred.get("recipient_name"),
            "achievement_name": achievement.get("name"),
            "issuer_name": issuer.get("name"),
            "issuer_id": issuer.get("issuer_id"),
            "issued_at": cred.get("valid_from"),
            "expires_at": cred.get("expires_at"),
            "signature_valid": True,
            "status_valid": True,
            "message": "Credential is authentic, valid, and cryptographically verified."
        }

    @classmethod
    async def verify_external_payload(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standards-compliant external verification of raw W3C VC or Open Badges v3 JSON documents.
        Validates structure, extracts verificationMethod, locates public key, and verifies signature.
        """
        if not isinstance(payload, dict):
            return {
                "valid": False,
                "verification_status": "MALFORMED",
                "message": "Credential payload must be a JSON object."
            }

        # Check essential standard fields
        if "@context" not in payload or "type" not in payload or "proof" not in payload:
            return {
                "valid": False,
                "verification_status": "MALFORMED",
                "message": "Missing required W3C VC fields (@context, type, or proof)."
            }

        proof = payload.get("proof")
        if not isinstance(proof, dict) or not proof.get("proofValue"):
            return {
                "valid": False,
                "verification_status": "MALFORMED",
                "message": "Proof block is missing or does not contain proofValue."
            }

        verification_method = proof.get("verificationMethod", "")
        # Expect format: .../issuers/{issuer_id}#keys-{key_id}
        public_key_pem: Optional[str] = None
        key_id = None
        issuer_id = None

        if "#keys-" in verification_method:
            parts = verification_method.split("#keys-")
            key_id = parts[1]
            issuer_part = parts[0].rstrip("/")
            issuer_id = issuer_part.split("/")[-1]

            key_doc = await CredentialKeyRepository.get_key_by_id(issuer_id, key_id)
            if key_doc:
                public_key_pem = key_doc.get("public_key")

        # Fallback: check if public key is embedded in proof
        if not public_key_pem and "publicKeyPem" in proof:
            public_key_pem = proof["publicKeyPem"]

        if not public_key_pem:
            return {
                "valid": False,
                "verification_status": "UNKNOWN_KEY",
                "message": f"Unable to resolve public key for verificationMethod '{verification_method}'."
            }

        sig_valid = CredentialSigningService.verify_payload_signature(payload, public_key_pem)
        if not sig_valid:
            return {
                "valid": False,
                "verification_status": "INVALID_SIGNATURE",
                "message": "Cryptographic signature validation FAILED."
            }

        # Check expiration
        now = datetime.now(timezone.utc)
        valid_until = payload.get("validUntil")
        if valid_until:
            try:
                dt = datetime.fromisoformat(str(valid_until).replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt < now:
                    return {
                        "valid": False,
                        "verification_status": "EXPIRED",
                        "expires_at": dt,
                        "message": "External credential has EXPIRED."
                    }
            except Exception:
                pass

        subject = payload.get("credentialSubject", {})
        recipient_name = subject.get("name") if isinstance(subject, dict) else None
        issuer_obj = payload.get("issuer", {})
        issuer_name = issuer_obj.get("name") if isinstance(issuer_obj, dict) else str(issuer_obj)

        return {
            "valid": True,
            "verification_status": "VALID",
            "credential_id": payload.get("id"),
            "recipient_name": recipient_name,
            "issuer_name": issuer_name,
            "issuer_id": issuer_id,
            "signature_valid": True,
            "status_valid": True,
            "message": "External credential successfully verified."
        }
