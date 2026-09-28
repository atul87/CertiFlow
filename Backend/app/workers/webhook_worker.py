"""
Webhook Delivery Worker (P8).
Asynchronously delivers signed HTTP webhook payloads with exponential retry backoff.
"""
from __future__ import annotations
import json
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import httpx

from app.core.config import settings
from app.repositories.webhook_repository import WebhookRepository
from app.security.webhooks import WebhookSecurity

logger = logging.getLogger(__name__)


async def deliver_webhook_task(
    ctx: Optional[Dict[str, Any]],
    delivery_id: str,
    org_id: str,
) -> Optional[Dict[str, Any]]:
    delivery = await WebhookRepository.get_delivery(delivery_id, org_id)
    if not delivery:
        logger.error(f"[WebhookWorker] Delivery {delivery_id} not found")
        return None

    endpoint_id = str(delivery["webhook_endpoint_id"])
    endpoint = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
    if not endpoint or endpoint.get("status") != "active":
        logger.warning(f"[WebhookWorker] Endpoint {endpoint_id} is disabled or missing")
        return await WebhookRepository.update_delivery(delivery_id, {
            "status": "cancelled",
            "error": "Endpoint disabled or deleted",
        })

    event_id = delivery["event_id"]
    event = await WebhookRepository.get_event(event_id)
    event_data = event.get("data", {}) if event else {}

    # Format webhook payload
    now = datetime.now(timezone.utc)
    ts = int(now.timestamp())
    payload = {
        "id": event_id,
        "type": delivery["event_type"],
        "version": "2026-09-01",
        "created_at": now.isoformat(),
        "data": event_data,
    }
    payload_str = json.dumps(payload, separators=(',', ':'), default=str)

    # Calculate HMAC-SHA256 signature
    secret = endpoint.get("secret_hash", "")  # Or use secret key if stored
    signature = WebhookSecurity.calculate_signature(secret, ts, payload_str)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CertiFlow-Webhooks/1.0",
        "X-Webhook-Signature": signature,
        "X-Webhook-Timestamp": str(ts),
        "X-Webhook-Event-Id": event_id,
    }

    url = endpoint["url"]
    t0 = time.monotonic()
    http_status = None
    error_msg = None
    success = False

    try:
        async with httpx.AsyncClient(timeout=settings.WEBHOOK_TIMEOUT_SECONDS, follow_redirects=False) as client:
            resp = await client.post(url, content=payload_str, headers=headers)
            http_status = resp.status_code
            duration_ms = round((time.monotonic() - t0) * 1000, 1)

            if 200 <= resp.status_code < 300:
                success = True
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        duration_ms = round((time.monotonic() - t0) * 1000, 1)
        error_msg = f"Delivery failed: {str(e)[:250]}"

    attempt = delivery.get("attempt", 1)

    if success:
        logger.info(f"[WebhookWorker] Webhook delivery {delivery_id} succeeded in {duration_ms}ms (HTTP {http_status})")
        return await WebhookRepository.update_delivery(delivery_id, {
            "status": "delivered",
            "http_status": http_status,
            "response_time_ms": duration_ms,
            "delivered_at": datetime.now(timezone.utc),
            "error": None,
        })
    else:
        logger.warning(f"[WebhookWorker] Webhook delivery {delivery_id} failed on attempt {attempt}: {error_msg}")
        # Evaluate retry
        max_retries = settings.WEBHOOK_MAX_RETRIES
        can_retry = attempt < max_retries and (http_status is None or http_status >= 500 or http_status == 429)

        if can_retry:
            backoff_secs = settings.WEBHOOK_RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            next_retry = datetime.now(timezone.utc) + timedelta(seconds=backoff_secs)
            return await WebhookRepository.update_delivery(delivery_id, {
                "status": "retrying",
                "attempt": attempt + 1,
                "http_status": http_status,
                "response_time_ms": duration_ms,
                "error": error_msg,
                "next_retry_at": next_retry,
            })
        else:
            return await WebhookRepository.update_delivery(delivery_id, {
                "status": "failed",
                "http_status": http_status,
                "response_time_ms": duration_ms,
                "error": error_msg,
            })
