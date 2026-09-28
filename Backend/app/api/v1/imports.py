from typing import Optional, List, Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    File,
    Form,
    Query,
    Response,
    status
)
from app.api.deps import (
    get_current_user_and_org,
    get_client_ip,
    get_client_user_agent
)
from app.schemas.common import APIResponse
from app.schemas.imports import (
    ImportResponse,
    ImportListResponse,
    ImportPreviewResponse,
    ImportRowResponse,
    ConfirmMappingRequest,
    ValidationErrorItem
)
from app.services.import_service import ImportService

router = APIRouter(prefix="/imports", tags=["Imports & Datasets"])


@router.post(
    "",
    response_model=APIResponse[ImportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload CSV or Excel recipient dataset for a certificate template"
)
async def upload_import(
    request: Request,
    file: UploadFile = File(...),
    template_id: str = Form(..., description="Target certificate template ID"),
    template_version_id: Optional[str] = Form(None, description="Optional specific template version ID"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    content = await file.read()

    imported = await ImportService.create_and_parse_import(
        content=content,
        filename=file.filename or "recipients.csv",
        template_id=template_id,
        template_version_id=template_version_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(imported)


@router.get(
    "",
    response_model=APIResponse[ImportListResponse],
    summary="List organization dataset imports with pagination"
)
async def list_imports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status: uploaded, parsed, mapping_required, validated, ready, failed"),
    template_id: Optional[str] = Query(None, description="Filter by template ID"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    result = await ImportService.list_imports(
        org_id=context["org_id"],
        page=page,
        limit=limit,
        status=status,
        template_id=template_id
    )
    return APIResponse.ok(result)


@router.get(
    "/{import_id}",
    response_model=APIResponse[ImportResponse],
    summary="Get import status, row counters, and column profiling"
)
async def get_import(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    imp = await ImportService.get_import(import_id, context["org_id"])
    return APIResponse.ok(imp)


@router.get(
    "/{import_id}/progress",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get import processing and validation progress"
)
async def get_import_progress(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    imp = await ImportService.get_import(import_id, context["org_id"])
    total = imp.total_rows or 0
    processed = (imp.valid_rows + imp.invalid_rows + imp.warning_rows) if imp.status in ["validated", "ready"] else (total if imp.status == "mapping_required" else 0)
    pct = int((processed / total * 100)) if total > 0 else 0
    return APIResponse.ok({
        "status": imp.status,
        "processed_rows": processed,
        "total_rows": total,
        "percentage": pct
    })


@router.get(
    "/{import_id}/mapping",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get suggested or confirmed column-to-field mappings"
)
async def get_import_mapping(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    mapping_data = await ImportService.get_mapping(import_id, context["org_id"])
    return APIResponse.ok(mapping_data)


@router.post(
    "/{import_id}/mapping",
    response_model=APIResponse[ImportResponse],
    summary="Confirm column mapping and trigger row-level dataset validation"
)
async def confirm_mapping(
    import_id: str,
    data: ConfirmMappingRequest,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    res = await ImportService.confirm_mapping_and_validate(
        import_id=import_id,
        org_id=context["org_id"],
        data=data,
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(res)


@router.post(
    "/{import_id}/validate",
    response_model=APIResponse[ImportResponse],
    summary="Re-validate import rows against template requirements"
)
async def revalidate_import(
    import_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    existing_mapping = await ImportService.get_mapping(import_id, context["org_id"])
    mappings_list = existing_mapping.get("mappings", [])

    data = ConfirmMappingRequest(mappings=mappings_list)
    res = await ImportService.confirm_mapping_and_validate(
        import_id=import_id,
        org_id=context["org_id"],
        data=data,
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(res)


@router.get(
    "/{import_id}/preview",
    response_model=APIResponse[ImportPreviewResponse],
    summary="Preview first 20 recipient rows with validation status"
)
async def preview_import(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    prev = await ImportService.get_preview(import_id, context["org_id"])
    return APIResponse.ok(prev)


@router.get(
    "/{import_id}/rows",
    response_model=APIResponse[Dict[str, Any]],
    summary="List paginated recipient records with filter by status (valid, warning, error)"
)
async def list_import_rows(
    import_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter: valid, warning, error"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    rows_data = await ImportService.list_rows(
        import_id=import_id,
        org_id=context["org_id"],
        page=page,
        limit=limit,
        status=status
    )
    return APIResponse.ok(rows_data)


@router.get(
    "/{import_id}/errors",
    response_model=APIResponse[List[ImportRowResponse]],
    summary="Get all rows that failed validation with detailed error reasons"
)
async def get_import_errors(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    err_rows = await ImportService.get_error_rows(import_id, context["org_id"])
    return APIResponse.ok(err_rows)


@router.get(
    "/{import_id}/errors/download",
    summary="Download CSV error report for invalid rows"
)
async def download_error_csv(
    import_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    csv_content = await ImportService.generate_error_csv(import_id, context["org_id"])
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=errors_import_{import_id}.csv"}
    )


@router.post(
    "/{import_id}/replace",
    response_model=APIResponse[ImportResponse],
    summary="Replace current import dataset with a corrected file"
)
async def replace_import_file(
    import_id: str,
    request: Request,
    file: UploadFile = File(...),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    imp = await ImportService.get_import(import_id, context["org_id"])
    content = await file.read()

    new_imp = await ImportService.create_and_parse_import(
        content=content,
        filename=file.filename or imp.filename,
        template_id=imp.template_id,
        template_version_id=imp.template_version_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok(new_imp)


@router.post(
    "/{import_id}/cancel",
    response_model=APIResponse[Dict[str, str]],
    summary="Cancel active dataset import"
)
async def cancel_import(
    import_id: str,
    request: Request,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    ip = get_client_ip(request)
    ua = get_client_user_agent(request)
    await ImportService.cancel_import(
        import_id=import_id,
        org_id=context["org_id"],
        user_id=context["user_id"],
        ip_address=ip,
        user_agent=ua
    )
    return APIResponse.ok({"message": "Import cancelled successfully"})
