from __future__ import annotations
import logging
from typing import Dict, Any, Optional
from app.repositories.credential_repository import CredentialRepository
from app.repositories.credential_status_repository import CredentialStatusRepository
from app.repositories.credential_event_repository import CredentialEventRepository
from app.core.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class CredentialStatusService:
    @classmethod
    async def set_status(
        cls,
        credential_id: str,
        status: str,
        reason: Optional[str] = None,
        actor_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transitions credential status, synchronizes with status registry,
        and records immutable audit event.
        """
        updated_cred = await CredentialRepository.update_status(credential_id, status, reason)
        if not updated_cred:
            raise NotFoundError(message=f"Credential '{credential_id}' not found", code="CREDENTIAL_NOT_FOUND")

        # Update dedicated status registry
        await CredentialStatusRepository.set_status(credential_id, status, reason)

        # Record lifecycle audit event
        await CredentialEventRepository.record_event(
            credential_id=credential_id,
            event_type=f"credential.{status.lower()}",
            organization_id=organization_id or updated_cred.get("organization_id"),
            actor_id=actor_id,
            metadata={"reason": reason, "previous_status": updated_cred.get("status")}
        )
        logger.info("Updated credential %s status to %s (reason: %s)", credential_id, status, reason)
        return updated_cred

    @classmethod
    async def get_status(cls, credential_id: str) -> Dict[str, Any]:
        status_doc = await CredentialStatusRepository.get_status(credential_id)
        if status_doc:
            return status_doc
        cred = await CredentialRepository.get_by_credential_id(credential_id)
        if not cred:
            raise NotFoundError(message=f"Credential '{credential_id}' not found", code="CREDENTIAL_NOT_FOUND")
        return {
            "credential_id": credential_id,
            "status": cred.get("status", "active"),
            "reason": cred.get("revocation_reason")
        }

    @classmethod
    async def sync_revocation(
        cls,
        organization_id: str,
        certificate_id: str,
        reason: str,
        actor_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Synchronizes certificate revocation with digital credential.
        Prevents PDF certificate and machine-readable credential status from silently diverging.
        """
        cred = await CredentialRepository.get_by_certificate_id(certificate_id)
        if not cred:
            return None

        return await cls.set_status(
            credential_id=cred["credential_id"],
            status="revoked",
            reason=reason,
            actor_id=actor_id,
            organization_id=organization_id
        )

    @classmethod
    async def sync_restore(
        cls,
        organization_id: str,
        certificate_id: str,
        actor_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Restores a previously suspended/revoked credential if certificate is restored.
        """
        cred = await CredentialRepository.get_by_certificate_id(certificate_id)
        if not cred:
            return None

        return await cls.set_status(
            credential_id=cred["credential_id"],
            status="active",
            reason="Certificate restored by authority",
            actor_id=actor_id,
            organization_id=organization_id
        )
