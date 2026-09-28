from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.credentials.canonicalizer import canonicalize_json
from app.credentials.signers.ed25519_signer import Ed25519Signer
from app.credentials.serializers.w3c_vc import W3CVCSerializer
from app.repositories.credential_key_repository import CredentialKeyRepository
from app.repositories.credential_repository import CredentialRepository
from app.services.credential_key_service import CredentialKeyService
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class CredentialSigningService:
    @classmethod
    async def sign_credential(
        cls,
        credential: Dict[str, Any],
        issuer: Dict[str, Any],
        achievement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Signs canonical digital credential using the issuer's active Ed25519 private key.
        Produces W3C Data Integrity proof block (Ed25519Signature2020) and attaches it to the credential.
        """
        issuer_id = issuer["issuer_id"]
        key_doc = await CredentialKeyRepository.get_active_key(issuer_id)
        if not key_doc:
            key_doc = await CredentialKeyService.get_or_create_active_key(issuer_id, credential["organization_id"])

        encrypted_private = key_doc["encrypted_private_key"]
        key_id = key_doc["key_id"]

        # Generate canonical document representation (unsigned)
        doc = W3CVCSerializer.serialize(
            credential=credential,
            issuer=issuer,
            achievement=achievement,
            evidence_items=credential.get("evidence"),
            proof=None
        )

        # RFC 8785 canonical serialization
        canonical_bytes = canonicalize_json(doc)

        # Sign with Ed25519 private key
        sig_b64 = Ed25519Signer.sign_bytes(canonical_bytes, encrypted_private)

        verification_method = f"{issuer.get('issuer_url')}#keys-{key_id}"
        proof = {
            "type": "Ed25519Signature2020",
            "created": datetime.now(timezone.utc).isoformat(),
            "verificationMethod": verification_method,
            "proofPurpose": "assertionMethod",
            "proofValue": sig_b64
        }

        # Store proof on credential document
        await CredentialRepository.attach_proof(credential["credential_id"], proof)
        logger.info("Successfully signed credential %s with key %s", credential["credential_id"], key_id)
        return proof

    @classmethod
    def verify_payload_signature(cls, payload: Dict[str, Any], public_key_pem: str) -> bool:
        """
        Cryptographically verifies the detached signature of an arbitrary W3C VC or Open Badge.
        Uses RFC 8785 canonicalization (which excludes the detached 'proof' block).
        """
        proof = payload.get("proof")
        if not proof or not isinstance(proof, dict):
            return False

        proof_value = proof.get("proofValue")
        if not proof_value or not isinstance(proof_value, str):
            return False

        # Canonicalize payload without the proof block
        canonical_bytes = canonicalize_json(payload)
        return Ed25519Signer.verify_bytes(canonical_bytes, proof_value, public_key_pem)
