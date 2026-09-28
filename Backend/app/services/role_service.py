"""
Custom role management service (P8).
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List

from app.core.exceptions import NotFoundError, ValidationError, ConflictError, ForbiddenError
from app.core.permissions import PERMISSIONS, SYSTEM_ROLE_PERMISSIONS
from app.repositories.role_repository import RoleRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.audit_log_repository import AuditLogRepository


class RoleService:
    @classmethod
    async def create_role(
        cls,
        org_id: str,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_name = name.strip()
        if clean_name.lower() in SYSTEM_ROLE_PERMISSIONS:
            raise ConflictError(message=f"'{clean_name}' is a reserved system role", code="RESERVED_ROLE_NAME")

        existing = await RoleRepository.get_by_name(org_id, clean_name)
        if existing:
            raise ConflictError(message=f"Role '{clean_name}' already exists in this organization", code="ROLE_EXISTS")

        # Validate requested permissions
        invalid_perms = set(permissions) - PERMISSIONS
        if invalid_perms:
            raise ValidationError(
                message=f"Invalid permissions specified: {', '.join(sorted(invalid_perms))}",
                code="INVALID_PERMISSIONS",
            )

        role = await RoleRepository.create(
            org_id=org_id,
            name=clean_name,
            permissions=permissions,
            description=description,
            is_system_role=False,
        )

        if user_id:
            await AuditLogRepository.log_event(
                action="role.created",
                resource_type="role",
                resource_id=role["id"],
                organization_id=org_id,
                user_id=user_id,
                metadata={"name": clean_name, "permissions": permissions},
            )

        return role

    @classmethod
    async def list_roles(cls, org_id: str) -> List[Dict[str, Any]]:
        # 1. System roles
        system_roles = []
        for s_name, s_perms in SYSTEM_ROLE_PERMISSIONS.items():
            count = await MemberRepository.count_members_with_role(org_id, s_name)
            system_roles.append({
                "id": f"sys_{s_name}",
                "organization_id": org_id,
                "name": s_name.capitalize(),
                "description": f"Built-in {s_name} role",
                "permissions": sorted(list(s_perms)),
                "is_system_role": True,
                "member_count": count,
            })

        # 2. Custom organization roles
        custom_roles = await RoleRepository.list_roles(org_id)
        for cr in custom_roles:
            cr["member_count"] = await MemberRepository.count_members_with_role(org_id, cr["name"])

        return system_roles + custom_roles

    @classmethod
    async def get_role(cls, role_id: str, org_id: str) -> Dict[str, Any]:
        if role_id.startswith("sys_"):
            s_name = role_id.replace("sys_", "")
            if s_name in SYSTEM_ROLE_PERMISSIONS:
                count = await MemberRepository.count_members_with_role(org_id, s_name)
                return {
                    "id": role_id,
                    "organization_id": org_id,
                    "name": s_name.capitalize(),
                    "description": f"Built-in {s_name} role",
                    "permissions": sorted(list(SYSTEM_ROLE_PERMISSIONS[s_name])),
                    "is_system_role": True,
                    "member_count": count,
                }

        role = await RoleRepository.get_by_id(role_id, org_id)
        if not role:
            raise NotFoundError(message="Role not found", code="ROLE_NOT_FOUND")
        role["member_count"] = await MemberRepository.count_members_with_role(org_id, role["name"])
        return role

    @classmethod
    async def update_role(
        cls,
        role_id: str,
        org_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if role_id.startswith("sys_"):
            raise ForbiddenError(message="System roles cannot be modified", code="CANNOT_MODIFY_SYSTEM_ROLE")

        role = await RoleRepository.get_by_id(role_id, org_id)
        if not role:
            raise NotFoundError(message="Role not found", code="ROLE_NOT_FOUND")

        if updates.get("permissions") is not None:
            invalid_perms = set(updates["permissions"]) - PERMISSIONS
            if invalid_perms:
                raise ValidationError(
                    message=f"Invalid permissions specified: {', '.join(sorted(invalid_perms))}",
                    code="INVALID_PERMISSIONS",
                )

        updated = await RoleRepository.update(role_id, org_id, updates)
        if user_id:
            await AuditLogRepository.log_event(
                action="role.updated",
                resource_type="role",
                resource_id=role_id,
                organization_id=org_id,
                user_id=user_id,
                metadata=updates,
            )
        return updated

    @classmethod
    async def delete_role(cls, role_id: str, org_id: str, user_id: Optional[str] = None) -> bool:
        if role_id.startswith("sys_"):
            raise ForbiddenError(message="System roles cannot be deleted", code="CANNOT_DELETE_SYSTEM_ROLE")

        role = await RoleRepository.get_by_id(role_id, org_id)
        if not role:
            raise NotFoundError(message="Role not found", code="ROLE_NOT_FOUND")

        # Check if active members are using this role
        active_users = await MemberRepository.count_members_with_role(org_id, role["name"])
        if active_users > 0:
            raise ForbiddenError(
                message=f"Cannot delete role '{role['name']}' because it is assigned to {active_users} member(s). Reassign them first.",
                code="ROLE_IN_USE",
            )

        success = await RoleRepository.delete(role_id, org_id)
        if success and user_id:
            await AuditLogRepository.log_event(
                action="role.deleted",
                resource_type="role",
                resource_id=role_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"name": role["name"]},
            )
        return success
