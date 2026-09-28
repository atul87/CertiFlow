from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Request, status
from app.api.deps import (
    get_current_user_and_org,
    get_current_org_id,
    require_role,
    get_client_ip,
    get_client_user_agent
)
from app.schemas.common import APIResponse
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
    OrganizationMemberResponse
)
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/me",
    response_model=APIResponse[OrganizationResponse],
    summary="Get current active organization details"
)
async def get_my_organization(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    org = await OrganizationService.get_user_organization(
        org_id=context["org_id"],
        user_id=context["user_id"]
    )
    return APIResponse.ok(org)


@router.patch(
    "/me",
    response_model=APIResponse[OrganizationResponse],
    summary="Update organization details (Owner/Admin only)"
)
async def update_my_organization(
    data: OrganizationUpdateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
    _role: str = Depends(require_role(["owner", "admin"]))
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    updated = await OrganizationService.update_organization(
        org_id=context["org_id"],
        user_id=context["user_id"],
        data=data,
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(updated)


@router.get(
    "/me/members",
    response_model=APIResponse[List[OrganizationMemberResponse]],
    summary="List members in the current active organization"
)
async def list_organization_members(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    members = await OrganizationService.list_members(
        org_id=context["org_id"],
        user_id=context["user_id"]
    )
    return APIResponse.ok(members)
