from __future__ import annotations
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.core.permissions import PERMISSIONS
from app.schemas.common import APIResponse
from app.schemas.role import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
)
from app.services.role_service import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get(
    "/permissions/registry",
    response_model=APIResponse[List[str]],
    summary="List all valid permission identifiers available in the system registry",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def get_permission_registry():
    return APIResponse.ok(sorted(list(PERMISSIONS)))


@router.get(
    "",
    response_model=APIResponse[RoleListResponse],
    summary="List all system and custom roles for the active organization",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def list_roles(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    roles = await RoleService.list_roles(org_id=org_id)
    return APIResponse.ok(
        RoleListResponse(
            items=[RoleResponse(**r) for r in roles],
            total=len(roles),
        )
    )


@router.post(
    "",
    response_model=APIResponse[RoleResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom role with defined permissions",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def create_role(
    data: RoleCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    role = await RoleService.create_role(
        org_id=org_id,
        name=data.name,
        permissions=data.permissions,
        description=data.description,
        user_id=user_id,
    )
    return APIResponse.created(RoleResponse(**role))


@router.get(
    "/{role_id}",
    response_model=APIResponse[RoleResponse],
    summary="Get details of a role",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def get_role(
    role_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    role = await RoleService.get_role(role_id=role_id, org_id=org_id)
    return APIResponse.ok(RoleResponse(**role))


@router.patch(
    "/{role_id}",
    response_model=APIResponse[RoleResponse],
    summary="Update a custom role's name, description, or permissions",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def update_role(
    role_id: str,
    data: RoleUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    updates = data.dict(exclude_unset=True)
    updated = await RoleService.update_role(
        role_id=role_id,
        org_id=org_id,
        updates=updates,
        user_id=user_id,
    )
    return APIResponse.ok(RoleResponse(**updated))


@router.delete(
    "/{role_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Delete a custom role (must not have any active assigned members)",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def delete_role(
    role_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await RoleService.delete_role(role_id=role_id, org_id=org_id, user_id=user_id)
    return APIResponse.ok({"deleted": True, "role_id": role_id})
