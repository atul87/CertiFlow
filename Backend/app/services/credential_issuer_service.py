from __future__ import annotations
import logging
from typing import Dict, Any, Optional, List
from app.repositories.issuer_repository import IssuerRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.credential_key_service import CredentialKeyService
from app.schemas.issuer import IssuerProfileUpdateRequest, PublicIssuerProfileResponse, PublicIssuerKeyInfo
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class CredentialIssuerService:
    @classmethod
    async def get_or_create_default_issuer(
        cls,
        organization_id: str,
        org_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve existing issuer profile for an organization, or provision a default one.
        Ensures active Ed25519 signing key is generated and attached.
        """
        issuer = await IssuerRepository.get_by_org_id(organization_id)
        if not issuer:
            if not org_name:
                org = await OrganizationRepository.get_by_id(organization_id)
                org_name = org.get("name") if org else "CertiFlow Issuing Authority"

            issuer = await IssuerRepository.create(
                organization_id=organization_id,
                name=org_name,
                description=f"Official digital credential issuing profile for {org_name}",
            )
            logger.info("Created default issuer %s for organization %s", issuer["issuer_id"], organization_id)

        # Ensure active signing key is provisioned
        if not issuer.get("active_key_id"):
            key_doc = await CredentialKeyService.get_or_create_active_key(issuer["issuer_id"], organization_id)
            issuer["active_key_id"] = key_doc["key_id"]

        return issuer

    @classmethod
    async def get_issuer_by_org(cls, organization_id: str) -> Dict[str, Any]:
        issuer = await IssuerRepository.get_by_org_id(organization_id)
        if not issuer:
            # Auto-create default issuer if organization exists
            return await cls.get_or_create_default_issuer(organization_id)
        return issuer

    @classmethod
    async def get_issuer_by_id(cls, issuer_id: str) -> Dict[str, Any]:
        issuer = await IssuerRepository.get_by_issuer_id(issuer_id)
        if not issuer:
            raise NotFoundError(message=f"Issuer profile '{issuer_id}' not found", code="ISSUER_NOT_FOUND")
        return issuer

    @classmethod
    async def update_issuer(cls, organization_id: str, data: IssuerProfileUpdateRequest) -> Dict[str, Any]:
        # Ensure issuer exists first
        await cls.get_or_create_default_issuer(organization_id)
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        updated = await IssuerRepository.update(organization_id, updates)
        if not updated:
            raise NotFoundError(message="Issuer profile not found", code="ISSUER_NOT_FOUND")
        return updated

    @classmethod
    async def rotate_keys(cls, organization_id: str) -> Dict[str, Any]:
        issuer = await cls.get_or_create_default_issuer(organization_id)
        new_key = await CredentialKeyService.rotate_keys(issuer["issuer_id"], organization_id)
        return new_key

    @classmethod
    async def get_public_issuer_profile(cls, issuer_id: str) -> Dict[str, Any]:
        issuer = await cls.get_issuer_by_id(issuer_id)
        public_keys = await CredentialKeyService.list_public_keys(issuer_id)
        return {
            "issuer_id": issuer["issuer_id"],
            "name": issuer["name"],
            "description": issuer.get("description"),
            "logo": issuer.get("logo"),
            "website": issuer.get("website"),
            "email": issuer.get("email"),
            "issuer_url": issuer["issuer_url"],
            "verification_url": issuer["verification_url"],
            "public_keys": [
                {
                    "key_id": k["key_id"],
                    "algorithm": k["algorithm"],
                    "public_key_pem": k["public_key"],
                    "status": k["status"],
                    "activated_at": k.get("activated_at", k.get("created_at"))
                }
                for k in public_keys
            ]
        }
