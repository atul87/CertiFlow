"""
Outbox Relay Worker — P12.22 & P12.23.
Asynchronously polls and delivers transactional outbox events with exponential backoff and dead-letter handling.
"""
from __future__ import annotations
import asyncio
import logging
from typing import Dict, Any, Optional

from app.repositories.outbox_repository import OutboxRepository

logger = logging.getLogger(__name__)


async def process_outbox_events_task(ctx: Optional[dict] = None, batch_size: int = 20) -> Dict[str, Any]:
    """
    ARQ / Background task that processes pending outbox events.
    """
    events = await OutboxRepository.claim_pending_events(batch_size=batch_size)
    if not events:
        return {"status": "ok", "processed": 0}

    delivered = 0
    retried = 0
    dead_lettered = 0

    for ev in events:
        event_id = ev["event_id"]
        dest_type = ev.get("destination_type")
        payload = ev.get("payload", {})
        org_id = ev.get("organization_id")
        attempts = ev.get("attempts", 0)

        # Exponential backoff formula: 5s, 10s, 20s, 40s (capped at 300s)
        backoff_sec = min(300, 5 * (2 ** attempts))

        try:
            if dest_type == "webhook":
                delivery_id = payload.get("delivery_id")
                from app.workers.webhook_worker import deliver_webhook_task
                await deliver_webhook_task(ctx=None, delivery_id=delivery_id, org_id=org_id)
            elif dest_type == "email":
                cert_id = payload.get("certificate_id")
                user_id = payload.get("user_id")
                from app.services.email_service import EmailService
                await EmailService.send_certificate_email(
                    certificate_id=cert_id,
                    org_id=org_id,
                    user_id=user_id,
                )
            else:
                logger.warning("Unknown outbox destination_type: %s", dest_type)

            await OutboxRepository.mark_delivered(event_id)
            delivered += 1

        except Exception as exc:
            err_msg = str(exc)
            final_status = await OutboxRepository.record_failure(
                event_id=event_id,
                error_message=err_msg,
                backoff_seconds=backoff_sec,
            )
            if final_status == "dead_letter":
                dead_lettered += 1
            else:
                retried += 1

    logger.info("Processed outbox batch: delivered=%d, retried=%d, dead_letter=%d", delivered, retried, dead_lettered)
    return {
        "status": "ok",
        "processed": len(events),
        "delivered": delivered,
        "retried": retried,
        "dead_letter": dead_lettered,
    }
