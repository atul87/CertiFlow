from __future__ import annotations
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.team import (
    TeamCreateRequest,
    TeamUpdateRequest,
    TeamMemberAddRequest,
    TeamResponse,
    TeamListResponse,
    TeamMemberResponse,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get(
    "",
    response_model=APIResponse[TeamListResponse],
    summary="List all teams in the organization",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def list_teams(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    teams = await TeamService.list_teams(org_id=org_id)
    return APIResponse.ok(
        TeamListResponse(
            items=[TeamResponse(**t) for t in teams],
            total=len(teams),
        )
    )


@router.post(
    "",
    response_model=APIResponse[TeamResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def create_team(
    data: TeamCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    team = await TeamService.create_team(
        org_id=org_id,
        name=data.name,
        description=data.description,
        created_by=user_id,
    )
    return APIResponse.created(TeamResponse(**team))


@router.get(
    "/{team_id}",
    response_model=APIResponse[TeamResponse],
    summary="Get details of a team",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def get_team(
    team_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    team = await TeamService.get_team(team_id=team_id, org_id=org_id)
    return APIResponse.ok(TeamResponse(**team))


@router.patch(
    "/{team_id}",
    response_model=APIResponse[TeamResponse],
    summary="Update a team's name or description",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def update_team(
    team_id: str,
    data: TeamUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    updates = data.dict(exclude_unset=True)
    updated = await TeamService.update_team(
        team_id=team_id,
        org_id=org_id,
        updates=updates,
        user_id=user_id,
    )
    return APIResponse.ok(TeamResponse(**updated))


@router.delete(
    "/{team_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Delete a team",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def delete_team(
    team_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await TeamService.delete_team(team_id=team_id, org_id=org_id, user_id=user_id)
    return APIResponse.ok({"deleted": True, "team_id": team_id})


@router.get(
    "/{team_id}/members",
    response_model=APIResponse[List[TeamMemberResponse]],
    summary="List members in a team",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def list_team_members(
    team_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    members = await TeamService.list_members(team_id=team_id, org_id=org_id)
    return APIResponse.ok([TeamMemberResponse(**m) for m in members])


@router.post(
    "/{team_id}/members",
    response_model=APIResponse[TeamMemberResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a user to a team",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def add_team_member(
    team_id: str,
    data: TeamMemberAddRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    actor_id = context["user_id"]
    member = await TeamService.add_member(
        team_id=team_id,
        user_id=data.user_id,
        org_id=org_id,
        actor_id=actor_id,
        role=data.role or "member",
    )
    return APIResponse.created(TeamMemberResponse(**member))


@router.delete(
    "/{team_id}/members/{user_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Remove a user from a team",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def remove_team_member(
    team_id: str,
    user_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    actor_id = context["user_id"]
    await TeamService.remove_member(
        team_id=team_id,
        user_id=user_id,
        org_id=org_id,
        actor_id=actor_id,
    )
    return APIResponse.ok({"removed": True, "team_id": team_id, "user_id": user_id})
