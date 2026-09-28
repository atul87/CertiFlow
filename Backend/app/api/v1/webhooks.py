from __future__ import annotations
from typing import Optional, Dict, Any, List
import hmac
import hashlib
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Header, HTTPException, Depends, Query, status

from app.core.config import settings
from app.api.deps import (
    get_current_user_and_org,
    require_permission,
)
from app.schemas.common import APIResponse
from app.schemas.webhook import (
    WebhookEndpointCreateRequest,
    WebhookEndpointUpdateRequest,
    WebhookEndpointResponse,
    WebhookEndpointListResponse,
    WebhookDeliveryResponse,
    WebhookDeliveryListResponse,
    WebhookTestResponse,
)
from app.services.email_delivery_service import EmailDeliveryService
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhooks"])


def verify_signature(secret: str, body: bytes, signature_header: Optional[str]) -> bool:
    """Validate webhook HMAC SHA256 signature if secret is configured."""
    if not secret or not signature_header:
        if settings.APP_ENV in ("development", "test"):
            return True
        return False

    computed = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature_header.strip())


# ---------------------------------------------------------
# INBOUND EMAIL WEBHOOKS (P6)
# ---------------------------------------------------------
@router.post(
    "/webhooks/email/{provider}",
    summary="Receive provider webhook for delivery events",
)
async def receive_email_webhook(
    provider: str,
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature"),
):
    body = await request.body()
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    if settings.WEBHOOK_SIGNING_SECRET:
        if not verify_signature(settings.WEBHOOK_SIGNING_SECRET, body, x_webhook_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    logger.info(f"[Webhook] Received webhook from provider {provider}: {payload}")

    event_type = payload.get("event") or payload.get("type") or payload.get("event_type")
    provider_message_id = (
        payload.get("message_id")
        or payload.get("provider_message_id")
        or (payload.get("data") or {}).get("email_id")
    )
    provider_event_id = (
        payload.get("event_id")
        or payload.get("id")
        or (payload.get("data") or {}).get("event_id")
    )
    reason = payload.get("reason") or (payload.get("data") or {}).get("reason")

    if not event_type or not provider_message_id:
        return {"success": False, "message": "Missing event or message_id"}

    event_map = {
        "delivered": "delivered",
        "email.delivered": "delivered",
        "bounce": "bounced",
        "bounced": "bounced",
        "email.bounced": "bounced",
        "complaint": "complained",
        "complained": "complained",
        "email.complained": "complained",
    }
    normalized_event = event_map.get(event_type.lower())
    if not normalized_event:
        return {"success": True, "message": f"Ignored event type {event_type}"}

    result = await EmailDeliveryService.process_webhook_event(
        provider=provider,
        event_type=normalized_event,
        provider_message_id=str(provider_message_id),
        provider_event_id=str(provider_event_id) if provider_event_id else None,
        reason=str(reason) if reason else None,
        metadata=payload,
    )

    return {"success": True, "processed": result is not None}


# ---------------------------------------------------------
# OUTBOUND WEBHOOK SUBSCRIPTIONS & DELIVERIES (P8)
# ---------------------------------------------------------
@router.get(
    "/webhooks",
    response_model=APIResponse[WebhookEndpointListResponse],
    summary="List all webhook endpoints registered in the organization",
    dependencies=[Depends(require_permission("webhooks.read"))],
)
async def list_webhook_endpoints(
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    endpoints = await WebhookService.list_endpoints(org_id=org_id)
    return APIResponse.ok(
        WebhookEndpointListResponse(
            items=[WebhookEndpointResponse(**ep) for ep in endpoints],
            total=len(endpoints),
        )
    )


@router.post(
    "/webhooks",
    response_model=APIResponse[WebhookEndpointResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new outbound webhook endpoint subscription",
    dependencies=[Depends(require_permission("webhooks.create"))],
)
async def create_webhook_endpoint(
    data: WebhookEndpointCreateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    endpoint = await WebhookService.create_endpoint(
        org_id=org_id,
        url=data.url,
        events=data.events,
        description=data.description,
        user_id=user_id,
    )
    return APIResponse.created(WebhookEndpointResponse(**endpoint))


@router.get(
    "/webhooks/{endpoint_id}",
    response_model=APIResponse[WebhookEndpointResponse],
    summary="Get details of a webhook endpoint",
    dependencies=[Depends(require_permission("webhooks.read"))],
)
async def get_webhook_endpoint(
    endpoint_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    ep = await WebhookService.get_endpoint(endpoint_id=endpoint_id, org_id=org_id)
    return APIResponse.ok(WebhookEndpointResponse(**ep))


@router.patch(
    "/webhooks/{endpoint_id}",
    response_model=APIResponse[WebhookEndpointResponse],
    summary="Update a webhook endpoint's URL, events, status, or description",
    dependencies=[Depends(require_permission("webhooks.update"))],
)
async def update_webhook_endpoint(
    endpoint_id: str,
    data: WebhookEndpointUpdateRequest,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    updates = data.dict(exclude_unset=True)
    updated = await WebhookService.update_endpoint(
        endpoint_id=endpoint_id,
        org_id=org_id,
        updates=updates,
        user_id=user_id,
    )
    return APIResponse.ok(WebhookEndpointResponse(**updated))


@router.delete(
    "/webhooks/{endpoint_id}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Delete a webhook endpoint",
    dependencies=[Depends(require_permission("webhooks.delete"))],
)
async def delete_webhook_endpoint(
    endpoint_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await WebhookService.delete_endpoint(
        endpoint_id=endpoint_id,
        org_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok({"deleted": True, "endpoint_id": endpoint_id})


@router.post(
    "/webhooks/{endpoint_id}/test",
    response_model=APIResponse[WebhookTestResponse],
    summary="Send a test ping event to the webhook endpoint and report immediate result",
    dependencies=[Depends(require_permission("webhooks.create"))],
)
async def test_webhook_endpoint(
    endpoint_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    res = await WebhookService.send_test_webhook(endpoint_id=endpoint_id, org_id=org_id)
    return APIResponse.ok(WebhookTestResponse(**res))


@router.post(
    "/webhooks/{endpoint_id}/rotate-secret",
    response_model=APIResponse[WebhookEndpointResponse],
    summary="Rotate the HMAC signing secret for a webhook endpoint",
    dependencies=[Depends(require_permission("webhooks.update"))],
)
async def rotate_webhook_secret(
    endpoint_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    rotated = await WebhookService.rotate_secret(
        endpoint_id=endpoint_id,
        org_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok(WebhookEndpointResponse(**rotated))


@router.get(
    "/webhooks/{endpoint_id}/deliveries",
    response_model=APIResponse[WebhookDeliveryListResponse],
    summary="List delivery history and logs for a specific webhook endpoint",
    dependencies=[Depends(require_permission("webhooks.read"))],
)
async def list_endpoint_deliveries(
    endpoint_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    items, total = await WebhookService.list_deliveries(
        org_id=org_id,
        endpoint_id=endpoint_id,
        page=page,
        limit=limit,
    )
    return APIResponse.ok(
        WebhookDeliveryListResponse(
            items=[WebhookDeliveryResponse(**d) for d in items],
            total=total,
        )
    )


@router.post(
    "/webhook-deliveries/{delivery_id}/retry",
    response_model=APIResponse[Dict[str, Any]],
    summary="Manually retry a failed webhook delivery",
    dependencies=[Depends(require_permission("webhooks.create"))],
)
async def retry_webhook_delivery(
    delivery_id: str,
    context: Dict[str, Any] = Depends(get_current_user_and_org),
):
    org_id = context["org_id"]
    user_id = context["user_id"]
    await WebhookService.retry_delivery(
        delivery_id=delivery_id,
        org_id=org_id,
        user_id=user_id,
    )
    return APIResponse.ok({"retried": True, "delivery_id": delivery_id})
