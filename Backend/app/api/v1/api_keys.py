from __future__ import annotations
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status

from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.api_key import (
    APIKeyCreateRequest,
    APIKeyResponse,
    APIKeyListResponse,
)
from app.services.api_key_service import APIKeyService

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get(
    "",
    response_model=APIResponse[APIKeyListResponse],
    summary="List all API keys for the current organization",
    dependencies=[Depends(require_permission("api_keys.read"))],
)
async def list_api_keys(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    keys = await APIKeyService.list_keys(org_id=org_id)
    return APIResponse.ok(
        APIKeyListResponse(
            items=[APIKeyResponse(**k) for k in keys],
            total=len(keys),
        )
    )


@router.post(
    "",
    response_model=APIResponse[APIKeyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new API key (secret key will be returned only once)",
    dependencies=[Depends(require_permission("api_keys.create"))],
)
async def create_api_key(
    data: APIKeyCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    key_doc = await APIKeyService.create_key(
        org_id=org_id,
        name=data.name,
        scopes=data.scopes,
        created_by=user_id,
        service_account_id=data.service_account_id,
        expires_in_days=data.expires_in_days,
    )
    return APIResponse.created(APIKeyResponse(**key_doc))


@router.get(
    "/{key_id}",
    response_model=APIResponse[APIKeyResponse],
    summary="Get details of an API key (never reveals plaintext secret)",
    dependencies=[Depends(require_permission("api_keys.read"))],
)
async def get_api_key(
    key_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    key_doc = await APIKeyService.get_key(key_id=key_id, org_id=org_id)
    return APIResponse.ok(APIKeyResponse(**key_doc))


@router.post(
    "/{key_id}/revoke",
    response_model=APIResponse[APIKeyResponse],
    summary="Revoke an API key immediately",
    dependencies=[Depends(require_permission("api_keys.revoke"))],
)
async def revoke_api_key(
    key_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    key_doc = await APIKeyService.revoke_key(key_id=key_id, org_id=org_id, user_id=user_id)
    return APIResponse.ok(APIKeyResponse(**key_doc))


@router.delete(
    "/{key_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Delete an API key record",
    dependencies=[Depends(require_permission("api_keys.revoke"))],
)
async def delete_api_key(
    key_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await APIKeyService.delete_key(key_id=key_id, org_id=org_id, user_id=user_id)
    return APIResponse.ok({"deleted": True, "key_id": key_id})
