from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
    require_role,
)
from app.core.exceptions import ForbiddenError, NotFoundError
from app.core.security import create_access_token, create_refresh_token
from app.repositories.member_repository import MemberRepository
from app.schemas.common import APIResponse
from app.schemas.member import (
    MemberResponse,
    MemberListResponse,
    MemberUpdateRequest,
    OwnershipTransferRequest,
)
from app.services.member_service import MemberService

router = APIRouter(tags=["Members"])


class SwitchOrgRequest(BaseModel):
    organization_id: str


@router.get(
    "/organization/members",
    response_model=APIResponse[MemberListResponse],
    summary="List organization members with pagination and status filter",
    dependencies=[Depends(require_permission("members.read"))],
)
@router.get(
    "/organizations/members",
    response_model=APIResponse[MemberListResponse],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.read"))],
)
async def list_members(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    items, total = await MemberService.list_members(
        org_id=org_id, page=page, limit=limit, status=status
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    resp = MemberListResponse(
        items=[MemberResponse(**m) for m in items],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )
    return APIResponse.ok(resp)


@router.patch(
    "/organization/members/{member_id}",
    response_model=APIResponse[MemberResponse],
    summary="Update member role or suspension status",
    dependencies=[Depends(require_permission("members.update"))],
)
@router.patch(
    "/organizations/members/{member_id}",
    response_model=APIResponse[MemberResponse],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.update"))],
)
async def update_member(
    member_id: str,
    data: MemberUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    actor_id = context["user_id"]
    updated = await MemberService.update_member(
        member_id=member_id,
        org_id=org_id,
        actor_user_id=actor_id,
        role=data.role,
        status=data.status,
    )
    return APIResponse.ok(MemberResponse(**updated))


@router.delete(
    "/organization/members/{member_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Remove a member from the organization",
    dependencies=[Depends(require_permission("members.remove"))],
)
@router.delete(
    "/organizations/members/{member_id}",
    response_model=APIResponse[Dict[str, Any]],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.remove"))],
)
async def remove_member(
    member_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    actor_id = context["user_id"]
    await MemberService.remove_member(
        member_id=member_id,
        org_id=org_id,
        actor_user_id=actor_id,
    )
    return APIResponse.ok({"removed": True, "member_id": member_id})


@router.post(
    "/organization/transfer-ownership",
    response_model=APIResponse[Dict[str, Any]],
    summary="Transfer organization ownership to an active member",
    dependencies=[Depends(require_role(["owner"]))],
)
@router.post(
    "/organizations/transfer-ownership",
    response_model=APIResponse[Dict[str, Any]],
    include_in_schema=False,
    dependencies=[Depends(require_role(["owner"]))],
)
async def transfer_ownership(
    data: OwnershipTransferRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    current_owner_id = context["user_id"]
    result = await MemberService.transfer_ownership(
        org_id=org_id,
        current_owner_id=current_owner_id,
        new_owner_user_id=data.new_owner_user_id,
    )
    return APIResponse.ok({"transferred": True, "new_owner_id": data.new_owner_user_id})


@router.post(
    "/organization/switch",
    response_model=APIResponse[Dict[str, Any]],
    summary="Switch active organization context and issue new scoped session tokens",
)
@router.post(
    "/organizations/switch",
    response_model=APIResponse[Dict[str, Any]],
    include_in_schema=False,
)
async def switch_organization(
    data: SwitchOrgRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    user_id = context["user_id"]
    target_org_id = data.organization_id

    # Verify active membership in target organization
    mem = await MemberRepository.get_by_user_id(target_org_id, user_id)
    if not mem or mem.get("status") != "active":
        raise ForbiddenError(
            message="User is not an active member of the target organization",
            code="NOT_ORG_MEMBER",
        )

    access_token = create_access_token(user_id=user_id, org_id=target_org_id)
    refresh_token = create_refresh_token(user_id=user_id, org_id=target_org_id)

    return APIResponse.ok({
        "organization_id": target_org_id,
        "role": mem.get("role"),
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    })
