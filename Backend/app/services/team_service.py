"""
Team and team membership management service (P8).
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List

from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.repositories.team_repository import TeamRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.audit_log_repository import AuditLogRepository


class TeamService:
    @classmethod
    async def create_team(
        cls,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        clean_name = name.strip()
        existing = await TeamRepository.get_team_by_name(org_id, clean_name)
        if existing:
            raise ConflictError(message=f"Team '{clean_name}' already exists in this organization", code="TEAM_EXISTS")

        team = await TeamRepository.create_team(
            org_id=org_id,
            name=clean_name,
            description=description,
            created_by=created_by,
        )

        if created_by:
            await AuditLogRepository.log_event(
                action="team.created",
                resource_type="team",
                resource_id=team["id"],
                organization_id=org_id,
                user_id=created_by,
                metadata={"name": clean_name},
            )
        return team

    @classmethod
    async def list_teams(cls, org_id: str) -> List[Dict[str, Any]]:
        return await TeamRepository.list_teams(org_id)

    @classmethod
    async def get_team(cls, team_id: str, org_id: str) -> Dict[str, Any]:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")
        return team

    @classmethod
    async def update_team(
        cls,
        team_id: str,
        org_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")

        if updates.get("name"):
            clean_name = updates["name"].strip()
            existing = await TeamRepository.get_team_by_name(org_id, clean_name)
            if existing and existing["id"] != team_id:
                raise ConflictError(message=f"Team '{clean_name}' already exists", code="TEAM_EXISTS")
            updates["name"] = clean_name

        updated = await TeamRepository.update_team(team_id, org_id, updates)
        if user_id:
            await AuditLogRepository.log_event(
                action="team.updated",
                resource_type="team",
                resource_id=team_id,
                organization_id=org_id,
                user_id=user_id,
                metadata=updates,
            )
        return updated

    @classmethod
    async def delete_team(cls, team_id: str, org_id: str, user_id: Optional[str] = None) -> bool:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")

        success = await TeamRepository.delete_team(team_id, org_id)
        if success and user_id:
            await AuditLogRepository.log_event(
                action="team.deleted",
                resource_type="team",
                resource_id=team_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"name": team["name"]},
            )
        return success

    @classmethod
    async def add_member(
        cls,
        team_id: str,
        user_id: str,
        org_id: str,
        actor_id: Optional[str] = None,
        role: str = "member",
    ) -> Dict[str, Any]:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")

        # Verify target user is an active member of the organization
        org_mem = await MemberRepository.get_by_user_id(org_id, user_id)
        if not org_mem or org_mem.get("status") != "active":
            raise ValidationError(message="User must be an active organization member to join a team", code="USER_NOT_ORG_MEMBER")

        tm = await TeamRepository.add_team_member(team_id, user_id, org_id, role)
        if actor_id:
            await AuditLogRepository.log_event(
                action="team.member_added",
                resource_type="team",
                resource_id=team_id,
                organization_id=org_id,
                user_id=actor_id,
                metadata={"added_user_id": user_id, "role": role},
            )
        return tm

    @classmethod
    async def remove_member(
        cls,
        team_id: str,
        user_id: str,
        org_id: str,
        actor_id: Optional[str] = None,
    ) -> bool:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")

        success = await TeamRepository.remove_team_member(team_id, user_id, org_id)
        if success and actor_id:
            await AuditLogRepository.log_event(
                action="team.member_removed",
                resource_type="team",
                resource_id=team_id,
                organization_id=org_id,
                user_id=actor_id,
                metadata={"removed_user_id": user_id},
            )
        return success

    @classmethod
    async def list_members(cls, team_id: str, org_id: str) -> List[Dict[str, Any]]:
        team = await TeamRepository.get_team_by_id(team_id, org_id)
        if not team:
            raise NotFoundError(message="Team not found", code="TEAM_NOT_FOUND")
        return await TeamRepository.list_team_members(team_id, org_id)
