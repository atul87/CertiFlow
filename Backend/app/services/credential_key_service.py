from __future__ import annotations
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.repositories.credential_key_repository import CredentialKeyRepository
from app.repositories.issuer_repository import IssuerRepository
from app.credentials.signers.ed25519_signer import Ed25519Signer
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class CredentialKeyService:
    @classmethod
    async def get_or_create_active_key(cls, issuer_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Retrieve the current active signing key for the issuer.
        If no active key exists, generate and persist a fresh Ed25519 keypair.
        """
        active_key = await CredentialKeyRepository.get_active_key(issuer_id)
        if active_key:
            return active_key

        # Generate a new Ed25519 keypair
        public_pem, enc_private = Ed25519Signer.generate_keypair()
        key_doc = await CredentialKeyRepository.create_key(
            issuer_id=issuer_id,
            organization_id=organization_id,
            algorithm="Ed25519",
            public_key_pem=public_pem,
            encrypted_private_key=enc_private,
            status="active"
        )
        await IssuerRepository.set_active_key(organization_id, key_doc["key_id"])
        logger.info("Generated new active signing key %s for issuer %s", key_doc["key_id"], issuer_id)
        return key_doc

    @classmethod
    async def rotate_keys(cls, issuer_id: str, organization_id: str) -> Dict[str, Any]:
        """
        Retire currently active keys and generate a fresh Ed25519 active key.
        Historical keys remain in the database with status 'retired' so existing
        credentials signed by them remain verifiable.
        """
        # Retire old active keys
        await CredentialKeyRepository.retire_active_keys(issuer_id)

        # Generate new key
        public_pem, enc_private = Ed25519Signer.generate_keypair()
        new_key = await CredentialKeyRepository.create_key(
            issuer_id=issuer_id,
            organization_id=organization_id,
            algorithm="Ed25519",
            public_key_pem=public_pem,
            encrypted_private_key=enc_private,
            status="active"
        )
        await IssuerRepository.set_active_key(organization_id, new_key["key_id"])
        logger.info("Rotated signing keys for issuer %s. New active key: %s", issuer_id, new_key["key_id"])
        return new_key

    @classmethod
    async def resolve_public_key(cls, issuer_id: str, key_id: str) -> Optional[str]:
        """Lookup public key PEM by key_id for verification."""
        key_doc = await CredentialKeyRepository.get_key_by_id(issuer_id, key_id)
        if not key_doc:
            return None
        return key_doc.get("public_key")

    @classmethod
    async def list_public_keys(cls, issuer_id: str) -> List[Dict[str, Any]]:
        return await CredentialKeyRepository.list_public_keys(issuer_id)
