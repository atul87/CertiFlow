import logging
from typing import List, Optional
from app.core.exceptions import NotFoundError, ForbiddenError
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
    OrganizationMemberResponse
)

logger = logging.getLogger(__name__)


class OrganizationService:
    @classmethod
    async def get_user_organization(cls, org_id: str, user_id: str) -> OrganizationResponse:
        membership = await OrganizationRepository.get_user_membership(org_id=org_id, user_id=user_id)
        if not membership:
            raise ForbiddenError(
                message="You do not have access to this organization",
                code="ORG_ACCESS_DENIED"
            )

        org = await OrganizationRepository.get_by_id(org_id)
        if not org:
            raise NotFoundError(message="Organization not found", code="ORG_NOT_FOUND")

        return OrganizationResponse(**org)

    @classmethod
    async def update_organization(
        cls,
        org_id: str,
        user_id: str,
        data: OrganizationUpdateRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OrganizationResponse:
        membership = await OrganizationRepository.get_user_membership(org_id=org_id, user_id=user_id)
        if not membership:
            raise ForbiddenError(
                message="You do not have access to this organization",
                code="ORG_ACCESS_DENIED"
            )

        if membership.get("role") not in ["owner", "admin"]:
            raise ForbiddenError(
                message="Only organization owners or admins can modify settings",
                code="INSUFFICIENT_PERMISSIONS"
            )

        updates = {}
        if data.name is not None:
            updates["name"] = data.name

        if not updates:
            org = await OrganizationRepository.get_by_id(org_id)
            return OrganizationResponse(**org)

        updated_org = await OrganizationRepository.update(org_id, updates)
        if not updated_org:
            raise NotFoundError(message="Organization not found", code="ORG_NOT_FOUND")

        await AuditLogRepository.log_event(
            action="organization.updated",
            resource_type="organization",
            resource_id=org_id,
            organization_id=org_id,
            user_id=user_id,
            metadata=updates,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return OrganizationResponse(**updated_org)

    @classmethod
    async def list_members(cls, org_id: str, user_id: str) -> List[OrganizationMemberResponse]:
        membership = await OrganizationRepository.get_user_membership(org_id=org_id, user_id=user_id)
        if not membership:
            raise ForbiddenError(
                message="You do not have access to this organization",
                code="ORG_ACCESS_DENIED"
            )

        members = await OrganizationRepository.list_members(org_id)
        return [OrganizationMemberResponse(**m) for m in members]
