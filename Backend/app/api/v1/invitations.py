from __future__ import annotations
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.member import (
    MemberInviteRequest,
    MemberInviteResponse,
    MemberInviteListResponse,
    MemberAcceptInviteRequest,
)
from app.services.member_service import MemberService

router = APIRouter(tags=["Invitations"])


@router.post(
    "/organization/invitations",
    response_model=APIResponse[MemberInviteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Invite a new member to the organization",
    dependencies=[Depends(require_permission("members.invite"))],
)
@router.post(
    "/organizations/invitations",
    response_model=APIResponse[MemberInviteResponse],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.invite"))],
)
async def invite_member(
    data: MemberInviteRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    inv = await MemberService.invite_member(
        org_id=org_id,
        email=data.email,
        role=data.role,
        invited_by=user_id,
        expires_in_days=data.expires_in_days,
    )
    return APIResponse.created(MemberInviteResponse(**inv))


@router.get(
    "/organization/invitations",
    response_model=APIResponse[MemberInviteListResponse],
    summary="List all pending/historical invitations for the organization",
    dependencies=[Depends(require_permission("members.read"))],
)
@router.get(
    "/organizations/invitations",
    response_model=APIResponse[MemberInviteListResponse],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.read"))],
)
async def list_invitations(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    items = await MemberService.list_invitations(org_id=org_id)
    return APIResponse.ok(
        MemberInviteListResponse(
            items=[MemberInviteResponse(**i) for i in items],
            total=len(items),
        )
    )


@router.post(
    "/organization/invitations/{invitation_id}/resend",
    response_model=APIResponse[MemberInviteResponse],
    summary="Resend an invitation with a refreshed secure token",
    dependencies=[Depends(require_permission("members.invite"))],
)
@router.post(
    "/organizations/invitations/{invitation_id}/resend",
    response_model=APIResponse[MemberInviteResponse],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.invite"))],
)
async def resend_invitation(
    invitation_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    inv = await MemberService.resend_invitation(
        invitation_id=invitation_id,
        org_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok(MemberInviteResponse(**inv))


@router.delete(
    "/organization/invitations/{invitation_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Cancel/revoke a pending invitation",
    dependencies=[Depends(require_permission("members.invite"))],
)
@router.delete(
    "/organizations/invitations/{invitation_id}",
    response_model=APIResponse[Dict[str, Any]],
    include_in_schema=False,
    dependencies=[Depends(require_permission("members.invite"))],
)
async def cancel_invitation(
    invitation_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await MemberService.cancel_invitation(
        invitation_id=invitation_id,
        org_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok({"cancelled": True, "invitation_id": invitation_id})


@router.post(
    "/organization/invitations/accept",
    response_model=APIResponse[Dict[str, Any]],
    summary="Accept an invitation using the secure token and join the organization",
)
@router.post(
    "/organizations/invitations/accept",
    response_model=APIResponse[Dict[str, Any]],
    include_in_schema=False,
)
async def accept_invitation(data: MemberAcceptInviteRequest):
    result = await MemberService.accept_invitation(
        raw_token=data.token,
        name=data.name,
        password=data.password,
    )
    return APIResponse.ok(result)
