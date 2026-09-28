from __future__ import annotations
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, Query, status
from app.api.deps import get_current_user_and_org, require_superadmin, require_reauth
from app.schemas.common import APIResponse
from app.schemas.admin import (
    AdminPlatformOverviewResponse,
    AdminEntitlementGrantRequest,
    AdminSubscriptionOverrideRequest
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["SaaS Admin Operations"])


@router.get(
    "/overview",
    response_model=APIResponse[AdminPlatformOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get platform-wide SaaS overview, MRR, subscriptions, and global counters",
    dependencies=[Depends(require_superadmin)]
)
async def get_platform_overview(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    overview = await AdminService.get_platform_overview()
    return APIResponse.ok(overview)


@router.post(
    "/organizations/{organization_id}/subscription",
    status_code=status.HTTP_200_OK,
    summary="Manually override an organization's subscription plan and status (Admin Support)",
    dependencies=[Depends(require_superadmin), Depends(require_reauth)]
)
async def override_subscription(
    organization_id: str,
    data: AdminSubscriptionOverrideRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    updated = await AdminService.override_subscription(
        org_id=organization_id,
        plan_id=data.plan_id,
        status=data.status,
        reason=data.reason,
        admin_user_id=context.get("user_id")
    )
    return APIResponse.ok(updated)


@router.post(
    "/organizations/{organization_id}/entitlements/grant",
    status_code=status.HTTP_200_OK,
    summary="Grant temporary or promotional quota override to an organization",
    dependencies=[Depends(require_superadmin)]
)
async def grant_entitlement_override(
    organization_id: str,
    data: AdminEntitlementGrantRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    feature = data.feature or data.metric
    quantity = data.quantity if data.quantity is not None else data.additional_quantity
    duration = data.duration_days or data.expires_in_days or 30

    granted = await AdminService.grant_entitlement_override(
        org_id=organization_id,
        feature=feature or "max_certificates_monthly",
        quantity=quantity or 1000,
        reason=data.reason or "Admin support grant",
        expires_in_days=duration,
        admin_user_id=context.get("user_id")
    )
    return APIResponse.ok(granted)


@router.post(
    "/organizations/{organization_id}/suspend",
    status_code=status.HTTP_200_OK,
    summary="Suspend an organization for policy violation or non-payment",
    dependencies=[Depends(require_superadmin), Depends(require_reauth)]
)
async def suspend_organization(
    organization_id: str,
    reason: Optional[str] = Query("Administrative suspension"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    res = await AdminService.suspend_organization(
        org_id=organization_id,
        reason=reason or "Administrative suspension",
        admin_user_id=context.get("user_id")
    )
    return APIResponse.ok({"suspended": res, "is_active": False, "organization_id": organization_id})


@router.post(
    "/organizations/{organization_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restore a suspended organization to active standing",
    dependencies=[Depends(require_superadmin), Depends(require_reauth)]
)
async def restore_organization(
    organization_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    res = await AdminService.restore_organization(
        org_id=organization_id,
        admin_user_id=context.get("user_id")
    )
    return APIResponse.ok({"restored": res, "is_active": True, "organization_id": organization_id})
