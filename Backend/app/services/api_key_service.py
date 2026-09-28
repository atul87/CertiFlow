"""
API Key management service (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError
from app.core.permissions import API_SCOPE_PERMISSIONS
from app.repositories.api_key_repository import APIKeyRepository
from app.repositories.service_account_repository import ServiceAccountRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.security.api_keys import APIKeySecurity


class APIKeyService:
    @classmethod
    async def create_key(
        cls,
        org_id: str,
        name: str,
        scopes: List[str],
        created_by: str,
        service_account_id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
    ) -> Dict[str, Any]:
        # Validate scopes
        all_allowed_scopes = set(API_SCOPE_PERMISSIONS.keys()) | {"*"}
        invalid_scopes = set(scopes) - all_allowed_scopes
        if invalid_scopes:
            raise ValidationError(
                message=f"Invalid API key scopes: {', '.join(sorted(invalid_scopes))}",
                code="INVALID_SCOPES",
            )

        # Validate service account if specified
        if service_account_id:
            sa = await ServiceAccountRepository.get_by_id(service_account_id, org_id)
            if not sa:
                raise NotFoundError(message="Service account not found", code="SERVICE_ACCOUNT_NOT_FOUND")
            if sa.get("status") != "active":
                raise ValidationError(message="Service account is disabled", code="SERVICE_ACCOUNT_DISABLED")

        # Expiry
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        raw_key, key_hash, prefix = APIKeySecurity.generate_api_key(is_test=False)

        key_doc = await APIKeyRepository.create(
            org_id=org_id,
            name=name.strip(),
            key_hash=key_hash,
            prefix=prefix,
            scopes=scopes,
            created_by=created_by,
            service_account_id=service_account_id,
            expires_at=expires_at,
        )

        await AuditLogRepository.log_event(
            action="api_key.created",
            resource_type="api_key",
            resource_id=key_doc["id"],
            organization_id=org_id,
            user_id=created_by,
            metadata={"prefix": prefix, "scopes": scopes, "service_account_id": service_account_id},
        )

        key_doc["key"] = raw_key  # Returned only upon initial creation!
        return key_doc

    @classmethod
    async def list_keys(cls, org_id: str) -> List[Dict[str, Any]]:
        return await APIKeyRepository.list_by_org(org_id)

    @classmethod
    async def get_key(cls, key_id: str, org_id: str) -> Dict[str, Any]:
        key = await APIKeyRepository.get_by_id(key_id, org_id)
        if not key:
            raise NotFoundError(message="API key not found", code="API_KEY_NOT_FOUND")
        return key

    @classmethod
    async def revoke_key(cls, key_id: str, org_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        key = await APIKeyRepository.get_by_id(key_id, org_id)
        if not key:
            raise NotFoundError(message="API key not found", code="API_KEY_NOT_FOUND")

        revoked = await APIKeyRepository.revoke(key_id, org_id)
        if user_id:
            await AuditLogRepository.log_event(
                action="api_key.revoked",
                resource_type="api_key",
                resource_id=key_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"prefix": key.get("prefix")},
            )
        return revoked

    @classmethod
    async def delete_key(cls, key_id: str, org_id: str, user_id: Optional[str] = None) -> bool:
        key = await APIKeyRepository.get_by_id(key_id, org_id)
        if not key:
            raise NotFoundError(message="API key not found", code="API_KEY_NOT_FOUND")

        success = await APIKeyRepository.delete(key_id, org_id)
        if success and user_id:
            await AuditLogRepository.log_event(
                action="api_key.deleted",
                resource_type="api_key",
                resource_id=key_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"prefix": key.get("prefix")},
            )
        return success
