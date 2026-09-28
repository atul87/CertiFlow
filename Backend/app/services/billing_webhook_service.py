from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ValidationError
from app.billing.provider_adapter import BillingProviderAdapter
from app.repositories.billing_event_repository import BillingEventRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.invoice_service import InvoiceService

logger = logging.getLogger(__name__)


class BillingWebhookService:
    @classmethod
    async def process_webhook(
        cls,
        provider_name: str,
        raw_body: bytes,
        signature_header: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate, deduplicate, and process billing webhook notifications.
        Guarantees strict idempotency and atomic status updates.
        """
        provider = BillingProviderAdapter.get_provider()

        # 1. Signature Verification
        secret = settings.BILLING_WEBHOOK_SECRET
        if not provider.verify_webhook_signature(raw_body, signature_header or "", secret):
            raise UnauthorizedError(message="Invalid billing webhook signature", code="INVALID_WEBHOOK_SIGNATURE")

        # 2. Parse Event
        try:
            event = provider.parse_event(raw_body, signature_header)
        except Exception as e:
            raise ValidationError(message=f"Malformed billing webhook payload: {str(e)}", code="INVALID_PAYLOAD")

        event_id = str(event.get("id") or event.get("event_id"))
        event_type = str(event.get("type") or event.get("event_type"))
        data = event.get("data", {})
        org_id = data.get("organization_id") or data.get("metadata", {}).get("organization_id")

        # 3. Idempotency Check
        is_new, recorded_doc = await BillingEventRepository.record_event(
            provider=provider_name,
            event_id=event_id,
            event_type=event_type,
            payload=event,
            organization_id=org_id
        )

        if not is_new:
            logger.info("Billing webhook %s (%s) already processed; returning idempotent success.", event_id, event_type)
            return {
                "status": "already_processed",
                "received": True,
                "duplicate": True,
                "event_id": event_id,
                "idempotent": True
            }

        # 4. Event Dispatcher
        now = datetime.now(timezone.utc)

        if event_type == "checkout.completed":
            target_plan = data.get("plan_id", "starter")
            interval = data.get("billing_interval", "monthly")
            period_days = 365 if interval == "yearly" else 30
            period_end = now + timedelta(days=period_days)
            amount = int(data.get("amount", 0))

            if org_id:
                sub = await SubscriptionRepository.upsert_subscription(
                    organization_id=org_id,
                    plan_id=target_plan,
                    status="active",
                    billing_interval=interval,
                    current_period_start=now,
                    current_period_end=period_end,
                    provider=provider_name,
                    provider_subscription_id=data.get("subscription_id"),
                    cancel_at_period_end=False
                )

                if amount > 0:
                    inv_num = f"INV-{now.strftime('%Y%m')}-{event_id[:6].upper()}"
                    await InvoiceService.record_paid_invoice(
                        organization_id=org_id,
                        amount=amount,
                        invoice_number=inv_num,
                        currency=data.get("currency", "INR"),
                        subscription_id=sub.get("id"),
                        period_start=now,
                        period_end=period_end,
                        provider_invoice_id=data.get("invoice_id")
                    )

                await AuditLogRepository.log_event(
                    action="subscription.upgraded",
                    resource_type="subscription",
                    resource_id=sub.get("id"),
                    organization_id=org_id,
                    metadata={"plan_id": target_plan, "interval": interval, "event_id": event_id}
                )

        elif event_type in ("invoice.paid", "payment.succeeded"):
            amount = int(data.get("amount", 0))
            if org_id and amount > 0:
                inv_num = f"INV-{now.strftime('%Y%m')}-{event_id[:6].upper()}"
                await InvoiceService.record_paid_invoice(
                    organization_id=org_id,
                    amount=amount,
                    invoice_number=inv_num,
                    currency=data.get("currency", "INR"),
                    provider_invoice_id=data.get("invoice_id")
                )
                await SubscriptionRepository.update_status(org_id, "active")

        elif event_type in ("payment.failed", "invoice.payment_failed"):
            if org_id:
                await SubscriptionRepository.update_status(org_id, "past_due")
                await AuditLogRepository.log_event(
                    action="billing.payment_failed",
                    resource_type="subscription",
                    resource_id="billing",
                    organization_id=org_id,
                    metadata={"event_id": event_id, "reason": data.get("failure_reason")}
                )

        elif event_type in ("subscription.cancelled", "customer.subscription.deleted"):
            if org_id:
                await SubscriptionRepository.update_status(org_id, "cancelled", cancel_at_period_end=True)

        # 5. Mark Processed
        await BillingEventRepository.mark_processed(provider_name, event_id)

        return {
            "status": "processed",
            "received": True,
            "event_id": event_id,
            "event_type": event_type
        }
