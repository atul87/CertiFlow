"""
Authorization and RBAC evaluation engine (P8).
Resolves effective permissions for users, custom roles, and API key scopes.
"""
from __future__ import annotations
from typing import Set, Dict, Any, Optional, List, Tuple

from app.core.exceptions import ForbiddenError
from app.core.permissions import (
    PERMISSIONS,
    SYSTEM_ROLE_PERMISSIONS,
    API_SCOPE_PERMISSIONS,
    get_role_permissions,
)
from app.repositories.role_repository import RoleRepository
from app.repositories.member_repository import MemberRepository


class AuthorizationService:
    @classmethod
    async def get_user_effective_permissions(
        cls,
        org_id: str,
        user_id: str,
    ) -> Tuple[str, Set[str]]:
        """
        Resolve the user's role and all effective permissions within the organization.
        Returns:
            role_name: str (e.g. 'owner', 'admin', 'member', 'viewer', or custom role name)
            permissions: Set[str]
        """
        member = await MemberRepository.get_by_user_id(org_id=org_id, user_id=user_id)
        if not member:
            raise ForbiddenError(message="Not a member of this organization", code="ORG_ACCESS_DENIED")

        if member.get("status") == "suspended":
            raise ForbiddenError(message="Your membership in this organization is suspended", code="MEMBER_SUSPENDED")

        if member.get("status") == "removed":
            raise ForbiddenError(message="You have been removed from this organization", code="MEMBER_REMOVED")

        role_name = member.get("role", "member")

        # 1. System role
        if role_name in SYSTEM_ROLE_PERMISSIONS:
            return role_name, set(SYSTEM_ROLE_PERMISSIONS[role_name])

        # 2. Custom role lookup
        custom_role = await RoleRepository.get_by_name(org_id, role_name)
        if custom_role:
            perms = set(custom_role.get("permissions", [])) & PERMISSIONS
            return role_name, perms

        # Fallback to viewer
        return role_name, set(SYSTEM_ROLE_PERMISSIONS.get("viewer", set()))

    @classmethod
    def validate_api_key_scopes(
        cls,
        key_scopes: List[str],
        required_permission: str,
    ) -> bool:
        """
        Check if any of the API key's scopes map to the required permission.
        """
        for scope in key_scopes:
            if scope == "*":
                return True
            granted = API_SCOPE_PERMISSIONS.get(scope, set())
            if required_permission in granted:
                return True
        return False
