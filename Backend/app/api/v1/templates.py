from typing import Optional, List, Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    Form,
    Query,
    status
)
from app.api.deps import (
    get_current_user_and_org,
    require_role,
    get_client_ip,
    get_client_user_agent
)
from app.schemas.common import APIResponse
from app.schemas.template import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateResponse,
    TemplateListResponse,
    TemplateVersionCreateRequest,
    TemplateVersionUpdateRequest,
    TemplateVersionResponse,
    PreviewRequest,
    PreviewResponse
)
from app.schemas.asset import AssetResponse
from app.services.template_service import TemplateService
from app.services.asset_service import AssetService

router = APIRouter(prefix="/templates", tags=["Templates"])


# --------------------------------------------------------------------------
# Template CRUD & Actions
# --------------------------------------------------------------------------

@router.post(
    "",
    response_model=APIResponse[TemplateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new certificate template"
)
async def create_template(
    data: TemplateCreateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    template = await TemplateService.create_template(
        data=data,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(template)


@router.get(
    "",
    response_model=APIResponse[TemplateListResponse],
    summary="List organization certificate templates with pagination and search"
)
async def list_templates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name or description"),
    status: Optional[str] = Query("active", description="Filter by status: 'active', 'archived'"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    result = await TemplateService.list_templates(
        org_id=context["org_id"],
        page=page,
        limit=limit,
        search=search,
        status=status
    )
    return APIResponse.ok(result)


@router.get(
    "/{template_id}",
    response_model=APIResponse[TemplateResponse],
    summary="Get single template details with current active design version"
)
async def get_template(
    template_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    template = await TemplateService.get_template(
        template_id=template_id,
        org_id=context["org_id"]
    )
    return APIResponse.ok(template)


@router.patch(
    "/{template_id}",
    response_model=APIResponse[TemplateResponse],
    summary="Update template metadata (name, description)"
)
async def update_template(
    template_id: str,
    data: TemplateUpdateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    updated = await TemplateService.update_template(
        template_id=template_id,
        org_id=context["org_id"],
        data=data,
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(updated)


@router.post(
    "/{template_id}/duplicate",
    response_model=APIResponse[TemplateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate template and clone latest design version"
)
async def duplicate_template(
    template_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    duplicated = await TemplateService.duplicate_template(
        template_id=template_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(duplicated)


@router.post(
    "/{template_id}/archive",
    response_model=APIResponse[Dict[str, str]],
    summary="Archive template (Owner or Admin only)"
)
async def archive_template(
    template_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
    _role: str = Depends(require_role(["owner", "admin"]))
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    await TemplateService.archive_template(
        template_id=template_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok({"message": "Template archived successfully"})


# --------------------------------------------------------------------------
# Version Management & Publishing (Immutable after publish)
# --------------------------------------------------------------------------

@router.post(
    "/{template_id}/versions",
    response_model=APIResponse[TemplateVersionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new draft design version for a template"
)
async def create_template_version(
    template_id: str,
    data: TemplateVersionCreateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    version = await TemplateService.create_version(
        template_id=template_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        data=data,
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(version)


@router.get(
    "/{template_id}/versions",
    response_model=APIResponse[List[TemplateVersionResponse]],
    summary="List all historical and draft versions of a template"
)
async def list_template_versions(
    template_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    versions = await TemplateService.list_versions(
        template_id=template_id,
        org_id=context["org_id"]
    )
    return APIResponse.ok(versions)


@router.get(
    "/{template_id}/versions/{version_id}",
    response_model=APIResponse[TemplateVersionResponse],
    summary="Get single template version details, elements, and placeholders"
)
async def get_template_version(
    template_id: str,
    version_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    version = await TemplateService.get_version(
        version_id=version_id,
        template_id=template_id,
        org_id=context["org_id"]
    )
    return APIResponse.ok(version)


@router.put(
    "/{template_id}/versions/{version_id}",
    response_model=APIResponse[TemplateVersionResponse],
    summary="Save editor state to draft version (Fails if version is published)"
)
async def update_template_version(
    template_id: str,
    version_id: str,
    data: TemplateVersionUpdateRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    updated = await TemplateService.update_draft_version(
        version_id=version_id,
        template_id=template_id,
        org_id=context["org_id"],
        data=data,
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(updated)


@router.post(
    "/{template_id}/versions/{version_id}/publish",
    response_model=APIResponse[TemplateVersionResponse],
    summary="Publish draft version to production (Owner or Admin only)"
)
async def publish_template_version(
    template_id: str,
    version_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
    _role: str = Depends(require_role(["owner", "admin"]))
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    published = await TemplateService.publish_version(
        version_id=version_id,
        template_id=template_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(published)


# --------------------------------------------------------------------------
# Lightweight Preview Endpoint
# --------------------------------------------------------------------------

@router.post(
    "/{template_id}/preview",
    response_model=APIResponse[PreviewResponse],
    summary="Generate high-fidelity rendered preview with sample data substitution"
)
async def preview_template(
    template_id: str,
    data: PreviewRequest = PreviewRequest(),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    preview = await TemplateService.generate_preview(
        template_id=template_id,
        org_id=context["org_id"],
        sample_data=data.sample_data
    )
    return APIResponse.ok(preview)


# --------------------------------------------------------------------------
# Asset Uploads & Management (Background, Logo, Signature)
# --------------------------------------------------------------------------

@router.post(
    "/{template_id}/assets",
    response_model=APIResponse[AssetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload image asset (background, logo, signature, seal)"
)
async def upload_asset(
    template_id: str,
    request: Request,
    file: UploadFile = File(...),
    asset_type: str = Form("background", description="background, logo, signature, seal, watermark"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    content = await file.read()

    asset = await AssetService.upload_asset(
        content=content,
        filename=file.filename or "upload.png",
        asset_type=asset_type,
        org_id=context["org_id"],
        user_id=context["user_id"],
        template_id=template_id,
        content_type=file.content_type,
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(asset)


@router.get(
    "/{template_id}/assets",
    response_model=APIResponse[List[AssetResponse]],
    summary="List all assets associated with a template"
)
async def list_template_assets(
    template_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    assets = await AssetService.list_template_assets(
        template_id=template_id,
        org_id=context["org_id"]
    )
    return APIResponse.ok(assets)


@router.delete(
    "/{template_id}/assets/{asset_id}",
    response_model=APIResponse[Dict[str, str]],
    summary="Delete template asset (Owner or Admin only)"
)
async def delete_template_asset(
    template_id: str,
    asset_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
    _role: str = Depends(require_role(["owner", "admin"]))
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    await AssetService.delete_asset(
        asset_id=asset_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok({"message": "Asset deleted successfully"})
