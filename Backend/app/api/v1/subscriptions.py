from __future__ import annotations
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, status
from app.api.deps import get_current_user_and_org, require_role
from app.schemas.common import APIResponse
from app.schemas.subscription import (
    SubscriptionResponse,
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionCancelRequest,
    SubscriptionResumeResponse
)
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/subscription", tags=["Subscriptions"])


@router.get(
    "",
    response_model=APIResponse[SubscriptionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get active organization subscription, status, and renewal information"
)
async def get_subscription(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    sub = await SubscriptionService.get_subscription(context["org_id"])
    return APIResponse.ok(sub)


@router.post(
    "/checkout",
    response_model=APIResponse[CheckoutResponse],
    status_code=status.HTTP_200_OK,
    summary="Create checkout session for subscription purchase or tier upgrade",
    dependencies=[Depends(require_role(["owner", "admin"]))]
)
async def create_checkout_session(
    data: CheckoutRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    email = context.get("user", {}).get("email") or "billing@certiflow.io"
    checkout = await SubscriptionService.create_checkout_session(
        org_id=context["org_id"],
        data=data,
        user_email=email
    )
    return APIResponse.ok(checkout)


@router.post(
    "/cancel",
    response_model=APIResponse[SubscriptionResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel subscription (effective at end of current billing period)",
    dependencies=[Depends(require_role(["owner"]))]
)
async def cancel_subscription(
    data: SubscriptionCancelRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    updated = await SubscriptionService.cancel_subscription(
        org_id=context["org_id"],
        immediate=data.immediate,
        reason=data.reason,
        user_id=context.get("user_id")
    )
    return APIResponse.ok(updated)


@router.post(
    "/resume",
    response_model=APIResponse[SubscriptionResumeResponse],
    status_code=status.HTTP_200_OK,
    summary="Resume a subscription scheduled for cancellation at period end",
    dependencies=[Depends(require_role(["owner"]))]
)
async def resume_subscription(
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    res = await SubscriptionService.resume_subscription(
        org_id=context["org_id"],
        user_id=context.get("user_id")
    )
    return APIResponse.ok(res)
