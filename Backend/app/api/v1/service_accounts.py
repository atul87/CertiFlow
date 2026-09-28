from __future__ import annotations
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.service_account import (
    ServiceAccountCreateRequest,
    ServiceAccountUpdateRequest,
    ServiceAccountResponse,
    ServiceAccountListResponse,
)
from app.services.service_account_service import ServiceAccountService

router = APIRouter(prefix="/service-accounts", tags=["Service Accounts"])


@router.get(
    "",
    response_model=APIResponse[ServiceAccountListResponse],
    summary="List all service accounts in the organization",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def list_service_accounts(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    items = await ServiceAccountService.list_by_org(org_id=org_id)
    return APIResponse.ok(
        ServiceAccountListResponse(
            items=[ServiceAccountResponse(**i) for i in items],
            total=len(items),
        )
    )


@router.post(
    "",
    response_model=APIResponse[ServiceAccountResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new service account",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def create_service_account(
    data: ServiceAccountCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    sa = await ServiceAccountService.create(
        org_id=org_id,
        name=data.name,
        description=data.description,
        created_by=user_id,
    )
    return APIResponse.created(ServiceAccountResponse(**sa))


@router.get(
    "/{sa_id}",
    response_model=APIResponse[ServiceAccountResponse],
    summary="Get details of a service account",
    dependencies=[Depends(require_permission("organization.read"))],
)
async def get_service_account(
    sa_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    sa = await ServiceAccountService.get_by_id(sa_id=sa_id, org_id=org_id)
    return APIResponse.ok(ServiceAccountResponse(**sa))


@router.patch(
    "/{sa_id}",
    response_model=APIResponse[ServiceAccountResponse],
    summary="Update a service account's details or status",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def update_service_account(
    sa_id: str,
    data: ServiceAccountUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    updates = data.dict(exclude_unset=True)
    updated = await ServiceAccountService.update(
        sa_id=sa_id,
        org_id=org_id,
        updates=updates,
        user_id=user_id,
    )
    return APIResponse.ok(ServiceAccountResponse(**updated))


@router.delete(
    "/{sa_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Delete a service account",
    dependencies=[Depends(require_permission("organization.update"))],
)
async def delete_service_account(
    sa_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await ServiceAccountService.delete(sa_id=sa_id, org_id=org_id, user_id=user_id)
    return APIResponse.ok({"deleted": True, "service_account_id": sa_id})
