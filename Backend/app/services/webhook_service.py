"""
Webhook lifecycle, dispatching, and management service (P8).
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.webhook_repository import WebhookRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.security.webhooks import WebhookSecurity
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_DELIVER_WEBHOOK

logger = logging.getLogger(__name__)


class WebhookService:
    @classmethod
    async def create_endpoint(
        cls,
        org_id: str,
        url: str,
        events: List[str],
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Validate URL with SSRF checks (unless test env)
        if settings.APP_ENV != "test":
            clean_url = WebhookSecurity.validate_destination_url(url)
        else:
            clean_url = url.strip()

        raw_secret = WebhookSecurity.generate_secret()
        secret_hash = WebhookSecurity.hash_secret(raw_secret)

        endpoint = await WebhookRepository.create_endpoint(
            org_id=org_id,
            url=clean_url,
            events=events,
            secret_hash=secret_hash,
            description=description,
            created_by=user_id,
        )

        if user_id:
            await AuditLogRepository.log_event(
                action="webhook_endpoint.created",
                resource_type="webhook_endpoint",
                resource_id=endpoint["id"],
                organization_id=org_id,
                user_id=user_id,
                metadata={"url": clean_url, "events": events},
            )

        endpoint["secret"] = raw_secret  # Returned only upon initial creation!
        return endpoint

    @classmethod
    async def list_endpoints(cls, org_id: str) -> List[Dict[str, Any]]:
        return await WebhookRepository.list_endpoints_by_org(org_id)

    @classmethod
    async def get_endpoint(cls, endpoint_id: str, org_id: str) -> Dict[str, Any]:
        ep = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
        if not ep:
            raise NotFoundError(message="Webhook endpoint not found", code="WEBHOOK_ENDPOINT_NOT_FOUND")
        return ep

    @classmethod
    async def update_endpoint(
        cls,
        endpoint_id: str,
        org_id: str,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        ep = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
        if not ep:
            raise NotFoundError(message="Webhook endpoint not found", code="WEBHOOK_ENDPOINT_NOT_FOUND")

        if updates.get("url") and settings.APP_ENV != "test":
            updates["url"] = WebhookSecurity.validate_destination_url(updates["url"])

        updated = await WebhookRepository.update_endpoint(endpoint_id, org_id, updates)
        if user_id:
            await AuditLogRepository.log_event(
                action="webhook_endpoint.updated",
                resource_type="webhook_endpoint",
                resource_id=endpoint_id,
                organization_id=org_id,
                user_id=user_id,
                metadata=updates,
            )
        return updated

    @classmethod
    async def delete_endpoint(cls, endpoint_id: str, org_id: str, user_id: Optional[str] = None) -> bool:
        ep = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
        if not ep:
            raise NotFoundError(message="Webhook endpoint not found", code="WEBHOOK_ENDPOINT_NOT_FOUND")

        success = await WebhookRepository.delete_endpoint(endpoint_id, org_id)
        if success and user_id:
            await AuditLogRepository.log_event(
                action="webhook_endpoint.deleted",
                resource_type="webhook_endpoint",
                resource_id=endpoint_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={"url": ep.get("url")},
            )
        return success

    @classmethod
    async def rotate_secret(cls, endpoint_id: str, org_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        ep = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
        if not ep:
            raise NotFoundError(message="Webhook endpoint not found", code="WEBHOOK_ENDPOINT_NOT_FOUND")

        raw_secret = WebhookSecurity.generate_secret()
        secret_hash = WebhookSecurity.hash_secret(raw_secret)

        updated = await WebhookRepository.update_endpoint(endpoint_id, org_id, {"secret_hash": secret_hash})
        if user_id:
            await AuditLogRepository.log_event(
                action="webhook_endpoint.secret_rotated",
                resource_type="webhook_endpoint",
                resource_id=endpoint_id,
                organization_id=org_id,
                user_id=user_id,
            )
        updated["secret"] = raw_secret  # Returned only once!
        return updated

    @classmethod
    async def dispatch_event(
        cls,
        org_id: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> Optional[str]:
        """
        Dispatches an outbound webhook event to all subscribed active endpoints in the organization.
        """
        endpoints = await WebhookRepository.list_endpoints_for_event(org_id, event_type)
        if not endpoints:
            return None

        event_id = f"evt_{uuid.uuid4().hex[:16]}"
        await WebhookRepository.create_event(
            event_id=event_id,
            org_id=org_id,
            event_type=event_type,
            data=data,
        )

        for ep in endpoints:
            delivery = await WebhookRepository.create_delivery(
                org_id=org_id,
                endpoint_id=ep["id"],
                event_id=event_id,
                event_type=event_type,
            )
            delivery_id = delivery["id"]

            queued = await QueueManager.enqueue(TASK_DELIVER_WEBHOOK, delivery_id, org_id)
            if not queued and settings.APP_ENV != "test":
                from app.workers.webhook_worker import deliver_webhook_task
                asyncio.create_task(deliver_webhook_task(None, delivery_id, org_id))

        return event_id

    @classmethod
    async def send_test_webhook(cls, endpoint_id: str, org_id: str) -> Dict[str, Any]:
        ep = await WebhookRepository.get_endpoint_by_id(endpoint_id, org_id)
        if not ep:
            raise NotFoundError(message="Webhook endpoint not found", code="WEBHOOK_ENDPOINT_NOT_FOUND")

        event_id = f"evt_test_{uuid.uuid4().hex[:12]}"
        test_data = {
            "test": True,
            "message": "This is a test notification from CertiFlow webhook delivery engine.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await WebhookRepository.create_event(
            event_id=event_id,
            org_id=org_id,
            event_type="webhook.test",
            data=test_data,
        )

        delivery = await WebhookRepository.create_delivery(
            org_id=org_id,
            endpoint_id=endpoint_id,
            event_id=event_id,
            event_type="webhook.test",
        )
        delivery_id = delivery["id"]

        # Run delivery immediately
        from app.workers.webhook_worker import deliver_webhook_task
        res = await deliver_webhook_task(None, delivery_id, org_id)

        status_str = res.get("status") if res else "failed"
        return {
            "success": status_str == "delivered",
            "delivery_id": delivery_id,
            "http_status": res.get("http_status") if res else None,
            "message": f"Test webhook delivery finished with status: {status_str}",
        }

    @classmethod
    async def list_deliveries(
        cls,
        org_id: str,
        endpoint_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await WebhookRepository.list_deliveries(org_id=org_id, endpoint_id=endpoint_id, page=page, limit=limit)

    @classmethod
    async def retry_delivery(cls, delivery_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        delivery = await WebhookRepository.get_delivery(delivery_id, org_id)
        if not delivery:
            raise NotFoundError(message="Delivery log not found", code="DELIVERY_NOT_FOUND")

        await WebhookRepository.update_delivery(delivery_id, {"status": "queued"})
        queued = await QueueManager.enqueue(TASK_DELIVER_WEBHOOK, delivery_id, org_id)
        if not queued and settings.APP_ENV != "test":
            from app.workers.webhook_worker import deliver_webhook_task
            asyncio.create_task(deliver_webhook_task(None, delivery_id, org_id))

        await AuditLogRepository.log_event(
            action="webhook_delivery.retried",
            resource_type="webhook_delivery",
            resource_id=delivery_id,
            organization_id=org_id,
            user_id=user_id,
        )
        return delivery
