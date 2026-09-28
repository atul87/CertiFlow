from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user_and_org
from app.schemas.common import APIResponse
from app.schemas.imports import MappingProfileResponse, MappingProfileCreateRequest
from app.services.import_service import ImportService

router = APIRouter(prefix="/mapping-profiles", tags=["Mapping Profiles"])


@router.get(
    "",
    response_model=APIResponse[List[MappingProfileResponse]],
    summary="List saved column mapping profiles for this organization"
)
async def list_profiles(
    template_id: Optional[str] = Query(None, description="Filter profiles by template"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    profiles = await ImportService.list_mapping_profiles(
        org_id=context["org_id"],
        template_id=template_id
    )
    return APIResponse.ok(profiles)


@router.post(
    "",
    response_model=APIResponse[MappingProfileResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create reusable mapping profile"
)
async def create_profile(
    data: MappingProfileCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    profile = await ImportService.create_mapping_profile(
        data=data,
        org_id=context["org_id"]
    )
    return APIResponse.ok(profile)


@router.delete(
    "/{profile_id}",
    response_model=APIResponse[Dict[str, str]],
    summary="Delete saved mapping profile"
)
async def delete_profile(
    profile_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    await ImportService.delete_mapping_profile(
        profile_id=profile_id,
        org_id=context["org_id"]
    )
    return APIResponse.ok({"message": "Mapping profile deleted successfully"})
