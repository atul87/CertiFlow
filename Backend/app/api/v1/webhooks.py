from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, status
import hmac
import hashlib
import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.services.email_delivery_service import EmailDeliveryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/email", tags=["Email Webhooks"])


def verify_signature(secret: str, body: bytes, signature_header: Optional[str]) -> bool:
    """Validate webhook HMAC SHA256 signature if secret is configured."""
    if not secret or not signature_header:
        if settings.APP_ENV in ("development", "test"):
            return True
        return False

    computed = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature_header.strip())


@router.post(
    "/{provider}",
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

    # Signature verification
    if settings.WEBHOOK_SIGNING_SECRET:
        if not verify_signature(settings.WEBHOOK_SIGNING_SECRET, body, x_webhook_signature):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    logger.info(f"[Webhook] Received webhook from provider {provider}: {payload}")

    # Normalize payload across providers (Mock, Resend, SendGrid, SES, SMTP)
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

    # Map event names
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
