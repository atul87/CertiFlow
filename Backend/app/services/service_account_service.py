"""
Service Account management service (P8).
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List

from app.core.exceptions import NotFoundError, ConflictError
from app.repositories.service_account_repository import ServiceAccountRepository
from app.repositories.audit_log_repository import AuditLogRepository


class ServiceAccountService:
    @classmethod
    async def create(
        cls,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_name = name.strip()
        existing = await ServiceAccountRepository.get_by_name(org_id, clean_name)
        if existing:
            raise ConflictError(message=f"Service account '{clean_name}' already exists", code="SERVICE_ACCOUNT_EXISTS")

        sa = await ServiceAccountRepository.create(
            org_id=org_id,
            name=clean_name,
            description=description,
            created_by=created_by,
        )

        if created_by:
            await AuditLogRepository.log_event(
                action="service_account.created",
                resource_type="service_account",
                resource_id=sa["id"],
                organization_id=org_id,
                user_id=created_by,
                metadata={"name": clean_name},
            )
        return sa

    @classmethod
    async def list_by_org(cls, org_id: str) -> List[Dict[str, Any]]:
        return await ServiceAccountRepository.list_by_org(org_id)

    @classmethod
    async def get_by_id(cls, sa_id: str, org_id: str) -> Dict[str, Any]:
        sa = await ServiceAccountRepository.get_by_id(sa_id, org_id)
        if not sa:
            raise NotFoundError(message="Service account not found", code="SERVICE_ACCOUNT_NOT_FOUND")
        return sa

    @classmethod
    async def update(
        cls,
        sa_id: str,
        org_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        sa = await ServiceAccountRepository.get_by_id(sa_id, org_id)
        if not sa:
            raise NotFoundError(message="Service account not found", code="SERVICE_ACCOUNT_NOT_FOUND")

        if updates.get("name"):
            clean_name = updates["name"].strip()
            existing = await ServiceAccountRepository.get_by_name(org_id, clean_name)
            if existing and existing["id"] != sa_id:
                raise ConflictError(message=f"Service account '{clean_name}' already exists", code="SERVICE_ACCOUNT_EXISTS")
            updates["name"] = clean_name

        updated = await ServiceAccountRepository.update(sa_id, org_id, updates)
        if user_id:
            await AuditLogRepository.log_event(
                action="service_account.updated",
                resource_type="service_account",
                resource_id=sa_id,
                organization_id=org_id,
                user_id=user_id,
                metadata=updates,
            )
        return updated

    @classmethod
    async def delete(cls, sa_id: str, org_id: str, user_id: Optional[str] = None) -> bool:
        sa = await ServiceAccountRepository.get_by_id(sa_id, org_id)
        if not sa:
            raise NotFoundError(message="Service account not found", code="SERVICE_ACCOUNT_NOT_FOUND")

        success = await ServiceAccountRepository.delete(sa_id, org_id)
        if success and user_id:
            await AuditLogRepository.log_event(
                action="service_account.deleted",
                resource_type="service_account",
                resource_id=sa_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"name": sa["name"]},
            )
        return success
