from __future__ import annotations
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request, Header, Query, status
from app.api.deps import get_current_user_and_org, require_role
from app.schemas.common import APIResponse
from app.schemas.usage import UsageSummaryResponse
from app.schemas.invoice import InvoiceListResponse, InvoiceResponse
from app.services.usage_service import UsageService
from app.services.invoice_service import InvoiceService
from app.services.cost_service import CostService
from app.services.billing_webhook_service import BillingWebhookService

router = APIRouter(prefix="/billing", tags=["Billing & Usage"])


@router.get(
    "/usage",
    response_model=APIResponse[UsageSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get monthly usage metrics, progress meters, and threshold warning status"
)
async def get_usage_summary(
    period: Optional[str] = Query(None, description="Billing period in YYYY-MM format"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    usage = await UsageService.get_usage_summary(context["org_id"], period=period)
    return APIResponse.ok(usage)


@router.get(
    "/invoices",
    response_model=APIResponse[InvoiceListResponse],
    status_code=status.HTTP_200_OK,
    summary="List organization payment invoices and receipts",
    dependencies=[Depends(require_role(["owner", "admin"]))]
)
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    invoices = await InvoiceService.list_invoices(context["org_id"], skip=skip, limit=limit)
    return APIResponse.ok(invoices)


@router.get(
    "/invoices/{invoice_id}",
    response_model=APIResponse[InvoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get invoice details by ID",
    dependencies=[Depends(require_role(["owner", "admin"]))]
)
async def get_invoice(
    invoice_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    inv = await InvoiceService.get_invoice(invoice_id, context["org_id"])
    return APIResponse.ok(inv)


@router.get(
    "/cost-estimate",
    status_code=status.HTTP_200_OK,
    summary="Get estimated infrastructure computing and delivery costs for organization",
    dependencies=[Depends(require_role(["owner", "admin"]))]
)
async def get_cost_estimate(
    period: Optional[str] = Query(None, description="Billing period YYYY-MM"),
    context: Dict[str, Any] = Depends(get_current_user_and_org)
):
    costs = await CostService.get_org_cost_breakdown(context["org_id"], period=period)
    return APIResponse.ok(costs)


@router.post(
    "/webhooks/{provider}",
    summary="Receive and verify inbound billing webhook events from payment provider",
    status_code=status.HTTP_200_OK
)
async def receive_billing_webhook(
    provider: str,
    request: Request,
    signature: Optional[str] = Header(None, alias="X-Billing-Signature"),
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    mock_signature: Optional[str] = Header(None, alias="X-Mock-Signature"),
):
    sig = (
        signature
        or stripe_signature
        or mock_signature
        or request.headers.get("x-mock-signature")
        or request.headers.get("x-billing-signature")
        or request.headers.get("stripe-signature")
        or request.headers.get("x-razorpay-signature")
        or ""
    )
    body = await request.body()
    result = await BillingWebhookService.process_webhook(
        provider_name=provider,
        raw_body=body,
        signature_header=sig
    )
    return APIResponse.ok(result)
