from __future__ import annotations
import re
import os
import math
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.email_template_repository import EmailTemplateRepository
from app.repositories.email_settings_repository import EmailSettingsRepository
from app.repositories.email_event_repository import EmailEventRepository
from app.repositories.email_job_repository import EmailJobRepository
from app.repositories.email_suppression_repository import EmailSuppressionRepository
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.email_render_service import EmailRenderService
from app.services.signed_url_service import SignedUrlService
from app.services.storage_service import StorageService
from app.providers.base import EmailMessage, EmailAttachment
from app.providers.factory import get_email_provider

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Sanitize certificate filename to prevent directory traversal and invalid chars."""
    basename = os.path.basename(name)
    sanitized = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', basename)
    sanitized = sanitized.strip().replace(' ', '_')
    if not sanitized.lower().endswith(".pdf"):
        sanitized += ".pdf"
    return sanitized or "certificate.pdf"


class EmailDeliveryService:

    @classmethod
    async def process_delivery(cls, delivery_id: str) -> Optional[Dict[str, Any]]:
        """
        Process a single email delivery record.
        Invoked by the ARQ email worker.
        """
        # 1. Load delivery
        delivery = await EmailDeliveryRepository.get_by_id(delivery_id)
        if not delivery:
            logger.error(f"[EmailDeliveryService] Delivery {delivery_id} not found")
            return None

        if delivery.get("status") not in ("queued", "failed"):
            logger.info(f"[EmailDeliveryService] Delivery {delivery_id} status is {delivery.get('status')}, skipping")
            return delivery

        # 2. Claim delivery atomically
        claimed = await EmailDeliveryRepository.claim_for_sending(delivery_id)
        if not claimed:
            logger.warning(f"[EmailDeliveryService] Could not claim delivery {delivery_id} (already claimed or max attempts)")
            return delivery

        delivery = claimed
        org_id = delivery["organization_id"]
        recipient_email = delivery["recipient_email"]
        job_id = delivery.get("email_job_id")

        # 3. Check suppression list
        is_suppressed = await EmailSuppressionRepository.is_suppressed(org_id, recipient_email)
        if is_suppressed:
            logger.warning(f"[EmailDeliveryService] Email {recipient_email} is suppressed for org {org_id}")
            updated = await EmailDeliveryRepository.mark_failed(
                delivery_id=delivery_id,
                error_code="EMAIL_SUPPRESSED",
                message=f"Recipient {recipient_email} is on the organization suppression list",
                retryable=False,
            )
            await EmailEventRepository.log_event(
                delivery_id=delivery_id,
                event_type="failed",
                provider=delivery.get("provider", "mock"),
                metadata={"reason": "suppressed"},
            )
            if job_id:
                await EmailJobRepository.record_delivery_outcome(job_id, from_status="sending", to_status="failed")
            return updated

        # 4. Load Certificate
        cert = await CertificateRepository.get_by_id(delivery["certificate_id"], org_id)
        if not cert or cert.get("status") == "revoked":
            logger.warning(f"[EmailDeliveryService] Certificate {delivery['certificate_id']} missing or revoked")
            updated = await EmailDeliveryRepository.mark_failed(
                delivery_id=delivery_id,
                error_code="EMAIL_CERTIFICATE_NOT_FOUND_OR_REVOKED",
                message="Certificate does not exist or has been revoked",
                retryable=False,
            )
            if job_id:
                await EmailJobRepository.record_delivery_outcome(job_id, from_status="sending", to_status="failed")
            return updated

        # 5. Load Organization & Settings
        org = await OrganizationRepository.get_by_id(org_id) or {"name": "Issuer"}
        email_settings_doc = await EmailSettingsRepository.get_by_org(org_id)

        # 6. Load Template
        template_doc = None
        if delivery.get("template_id"):
            template_doc = await EmailTemplateRepository.get_by_id(delivery["template_id"], org_id)
        if not template_doc:
            template_doc = await EmailTemplateRepository.get_default_or_first(org_id)

        # Built-in fallback template if none found
        if not template_doc:
            template_doc = {
                "subject": "Congratulations {{recipient_name}} — Your Certificate",
                "html_body": (
                    "<p>Hello {{recipient_name}},</p>"
                    "<p>Congratulations! Your certificate <strong>{{certificate_number}}</strong> for "
                    "<strong>{{program_name}}</strong> has been issued.</p>"
                    "<p><a href=\"{{verification_url}}\">Verify Certificate</a></p>"
                    "<p><a href=\"{{download_url}}\">Download Certificate</a></p>"
                    "<p>Regards,<br>{{issuer_name}}</p>"
                ),
                "text_body": (
                    "Hello {{recipient_name}},\n\n"
                    "Congratulations! Your certificate {{certificate_number}} for {{program_name}} has been issued.\n\n"
                    "Verify: {{verification_url}}\n"
                    "Download: {{download_url}}\n\n"
                    "Regards,\n{{issuer_name}}"
                ),
            }

        # 7. Generate URLs
        verification_code = cert.get("verification_code") or cert.get("certificate_number", "")
        verification_url = f"{settings.BASE_URL}/verify/{verification_code}"
        download_url = SignedUrlService.generate_signed_download_url(
            certificate_id=cert["id"],
            organization_id=org_id,
            expires_in_hours=settings.SIGNED_URL_EXPIRY_HOURS,
            base_url=settings.BASE_URL,
        )

        # 8. Render Email
        try:
            rendered = EmailRenderService.render_email(
                template_doc=template_doc,
                recipient_data=cert.get("recipient", {}),
                certificate_data=cert,
                organization_data=org,
                verification_url=verification_url,
                download_url=download_url,
            )
        except Exception as e:
            logger.error(f"[EmailDeliveryService] Render error for delivery {delivery_id}: {e}")
            updated = await EmailDeliveryRepository.mark_failed(
                delivery_id=delivery_id,
                error_code="EMAIL_TEMPLATE_INVALID",
                message=f"Template rendering failed: {str(e)}",
                retryable=False,
            )
            if job_id:
                await EmailJobRepository.record_delivery_outcome(job_id, from_status="sending", to_status="failed")
            return updated

        # 9. Handle Attachments
        attachments: List[EmailAttachment] = []
        delivery_mode = delivery.get("delivery_mode", "link")
        if delivery_mode in ("attachment", "both"):
            storage_key = cert.get("storage_key") or cert.get("pdf_storage_key")
            if storage_key:
                try:
                    pdf_bytes = await StorageService.download_file(storage_key)
                    max_size_bytes = settings.MAX_EMAIL_ATTACHMENT_SIZE_MB * 1024 * 1024
                    if len(pdf_bytes) > max_size_bytes:
                        logger.warning(f"[EmailDeliveryService] PDF {storage_key} exceeds max size {settings.MAX_EMAIL_ATTACHMENT_SIZE_MB}MB, omitting attachment")
                    else:
                        recipient_name = cert.get("recipient", {}).get("name", "certificate")
                        clean_fn = sanitize_filename(f"{recipient_name}_{cert.get('certificate_number', 'cert')}.pdf")
                        attachments.append(EmailAttachment(
                            filename=clean_fn,
                            content=pdf_bytes,
                            content_type="application/pdf",
                        ))
                except Exception as e:
                    logger.warning(f"[EmailDeliveryService] Could not load attachment for cert {cert['id']}: {e}")

        # 10. Instantiate Provider & Prepare Message
        provider = get_email_provider(email_settings_doc)
        sender_name = (email_settings_doc or {}).get("sender_name") or settings.DEFAULT_SENDER_NAME
        sender_email = (email_settings_doc or {}).get("sender_email") or settings.DEFAULT_SENDER_EMAIL
        reply_to = (email_settings_doc or {}).get("reply_to")

        msg = EmailMessage(
            to_email=recipient_email,
            to_name=delivery.get("recipient_name", ""),
            from_name=sender_name,
            from_email=sender_email,
            reply_to=reply_to,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            attachments=attachments,
            headers={
                "X-Delivery-ID": delivery_id,
                "X-Certificate-ID": cert["id"],
            },
        )

        # 11. Send Email
        try:
            result = await provider.send_email(msg)
            if result.success:
                updated = await EmailDeliveryRepository.mark_sent(
                    delivery_id=delivery_id,
                    provider_message_id=result.message_id or f"msg_{delivery_id}",
                    provider=result.provider,
                )
                await EmailEventRepository.log_event(
                    delivery_id=delivery_id,
                    event_type="sent",
                    provider=result.provider,
                    metadata={"provider_message_id": result.message_id},
                )
                await CertificateRepository.update_email_delivery_status(
                    certificate_id=cert["id"],
                    status="sent",
                    delivery_id=delivery_id,
                )
                if job_id:
                    await EmailJobRepository.record_delivery_outcome(job_id, from_status="sending", to_status="sent")

                try:
                    from app.services.webhook_service import WebhookService
                    await WebhookService.dispatch_event(
                        org_id=str(org_id),
                        event_type="email.sent",
                        data={
                            "delivery_id": delivery_id,
                            "certificate_id": str(cert["id"]),
                            "recipient_email": delivery["recipient_email"],
                            "provider": result.provider,
                        },
                    )
                except Exception:
                    pass

                return updated
            else:
                return await cls._handle_failure(
                    delivery=delivery,
                    error_code=result.error_code or "EMAIL_PROVIDER_REJECTED",
                    error_message=result.error_message or "Provider rejected email",
                    retryable=result.retryable,
                )
        except Exception as e:
            logger.exception(f"[EmailDeliveryService] Exception sending delivery {delivery_id}: {e}")
            return await cls._handle_failure(
                delivery=delivery,
                error_code="EMAIL_PROVIDER_TIMEOUT",
                error_message=str(e),
                retryable=True,
            )

    @classmethod
    async def _handle_failure(
        cls,
        delivery: Dict[str, Any],
        error_code: str,
        error_message: str,
        retryable: bool,
    ) -> Dict[str, Any]:
        delivery_id = delivery["id"]
        attempts = delivery.get("attempts", 1)
        max_attempts = delivery.get("max_attempts", settings.EMAIL_MAX_RETRIES)
        job_id = delivery.get("email_job_id")

        can_retry = retryable and (attempts < max_attempts)
        next_retry_at = None
        if can_retry:
            delay_seconds = int(60 * math.pow(2, attempts - 1))  # 1 min, 2 min, 4 min...
            next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)

        updated = await EmailDeliveryRepository.mark_failed(
            delivery_id=delivery_id,
            error_code=error_code,
            message=error_message,
            retryable=can_retry,
            next_retry_at=next_retry_at,
        )
        await EmailEventRepository.log_event(
            delivery_id=delivery_id,
            event_type="failed",
            provider=delivery.get("provider", "mock"),
            metadata={
                "error_code": error_code,
                "message": error_message,
                "retryable": can_retry,
                "attempts": attempts,
            },
        )
        if not can_retry and job_id:
            await EmailJobRepository.record_delivery_outcome(job_id, from_status="sending", to_status="failed")

        return updated

    @classmethod
    async def process_webhook_event(
        cls,
        provider: str,
        event_type: str,
        provider_message_id: str,
        provider_event_id: Optional[str] = None,
        reason: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Handle normalized webhook event from an email provider.
        Supports: delivered, bounced, complained.
        """
        delivery = await EmailDeliveryRepository.get_by_provider_message_id(provider_message_id)
        if not delivery:
            logger.warning(f"[EmailDeliveryService] No delivery found for provider_message_id: {provider_message_id}")
            return None

        delivery_id = delivery["id"]
        org_id = delivery["organization_id"]
        recipient_email = delivery["recipient_email"]
        job_id = delivery.get("email_job_id")
        current_status = delivery.get("status")

        # 1. Log event idempotently
        event_doc, is_new = await EmailEventRepository.log_event(
            delivery_id=delivery_id,
            event_type=event_type,
            provider=provider,
            provider_event_id=provider_event_id,
            metadata=metadata or {"reason": reason},
            timestamp=timestamp,
        )
        if not is_new:
            logger.info(f"[EmailDeliveryService] Duplicate webhook event {provider_event_id} ignored")
            return delivery

        # 2. Update status according to event
        if event_type == "delivered":
            updated = await EmailDeliveryRepository.mark_delivered(delivery_id, timestamp=timestamp)
            await CertificateRepository.update_email_delivery_status(
                certificate_id=delivery["certificate_id"],
                status="delivered",
                delivery_id=delivery_id,
            )
            if job_id and current_status != "delivered":
                await EmailJobRepository.record_delivery_outcome(job_id, from_status=current_status, to_status="delivered")

            try:
                from app.services.webhook_service import WebhookService
                await WebhookService.dispatch_event(
                    org_id=str(org_id),
                    event_type="email.delivered",
                    data={
                        "delivery_id": delivery_id,
                        "certificate_id": str(delivery.get("certificate_id")),
                        "recipient_email": recipient_email,
                    },
                )
            except Exception:
                pass

            return updated

        elif event_type == "bounced":
            updated = await EmailDeliveryRepository.mark_bounced(delivery_id, reason=reason or "hard_bounce", timestamp=timestamp)
            await CertificateRepository.update_email_delivery_status(
                certificate_id=delivery["certificate_id"],
                status="bounced",
                delivery_id=delivery_id,
            )
            # Add to suppression list for hard bounces
            await EmailSuppressionRepository.add_suppression(org_id, recipient_email, reason="hard_bounce")
            if job_id and current_status != "bounced":
                await EmailJobRepository.record_delivery_outcome(job_id, from_status=current_status, to_status="bounced")

            try:
                from app.services.webhook_service import WebhookService
                await WebhookService.dispatch_event(
                    org_id=str(org_id),
                    event_type="email.bounced",
                    data={
                        "delivery_id": delivery_id,
                        "certificate_id": str(delivery.get("certificate_id")),
                        "recipient_email": recipient_email,
                        "reason": reason or "hard_bounce",
                    },
                )
            except Exception:
                pass

            return updated

        elif event_type == "complained":
            updated = await EmailDeliveryRepository.mark_complained(delivery_id, reason=reason or "complaint", timestamp=timestamp)
            await CertificateRepository.update_email_delivery_status(
                certificate_id=delivery["certificate_id"],
                status="complained",
                delivery_id=delivery_id,
            )
            # Add to suppression list for complaints
            await EmailSuppressionRepository.add_suppression(org_id, recipient_email, reason="complaint")
            return updated

        return delivery
