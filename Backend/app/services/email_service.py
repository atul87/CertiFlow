from __future__ import annotations
import asyncio
import logging
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.email_template_repository import EmailTemplateRepository
from app.repositories.email_settings_repository import EmailSettingsRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.email_render_service import EmailRenderService
from app.services.signed_url_service import SignedUrlService
from app.providers.base import EmailMessage
from app.providers.factory import get_email_provider
from app.queue.redis import QueueManager
from app.queue.tasks import TASK_SEND_CERTIFICATE_EMAIL
from app.workers.email_worker import send_certificate_email_task

logger = logging.getLogger(__name__)


class EmailService:

    @classmethod
    async def send_certificate_email(
        cls,
        certificate_id: str,
        org_id: str,
        template_id: Optional[str] = None,
        delivery_mode: str = "link",
        recipient_email_override: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        cert = await CertificateRepository.get_by_id(certificate_id, org_id)
        if not cert:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        if cert.get("status") == "revoked":
            raise ValidationError(message="Cannot email a revoked certificate", code="CERTIFICATE_REVOKED")

        recipient_data = cert.get("recipient", {})
        recipient_email = recipient_email_override or recipient_data.get("email")
        if not recipient_email:
            raise ValidationError(message="Recipient has no email address", code="NO_RECIPIENT_EMAIL")

        recipient_name = recipient_data.get("name") or "Recipient"

        # Create delivery record
        delivery = await EmailDeliveryRepository.create(
            organization_id=org_id,
            certificate_id=certificate_id,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            template_id=template_id,
            delivery_mode=delivery_mode,
            issuance_job_id=cert.get("issuance_job_id"),
        )
        delivery_id = delivery["id"]

        if user_id:
            await AuditLogRepository.log_event(
                action="email_delivery.created",
                resource_type="email_delivery",
                resource_id=delivery_id,
                organization_id=org_id,
                user_id=user_id,
                metadata={
                    "certificate_id": certificate_id,
                    "recipient_email": recipient_email,
                    "delivery_mode": delivery_mode,
                },
            )

        # Enqueue sending task
        queued = await QueueManager.enqueue(TASK_SEND_CERTIFICATE_EMAIL, delivery_id)
        if not queued and settings.APP_ENV != "test":
            logger.info(f"Redis queue unavailable; executing delivery {delivery_id} via asyncio task")
            asyncio.create_task(send_certificate_email_task(None, delivery_id))

        return delivery

    @classmethod
    async def resend_certificate_email(
        cls,
        certificate_id: str,
        org_id: str,
        template_id: Optional[str] = None,
        delivery_mode: str = "link",
        recipient_email_override: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a NEW email delivery record to resend a certificate, preserving audit history.
        """
        delivery = await cls.send_certificate_email(
            certificate_id=certificate_id,
            org_id=org_id,
            template_id=template_id,
            delivery_mode=delivery_mode,
            recipient_email_override=recipient_email_override,
            user_id=user_id,
        )

        if user_id:
            await AuditLogRepository.log_event(
                action="email_delivery.resend",
                resource_type="email_delivery",
                resource_id=delivery["id"],
                organization_id=org_id,
                user_id=user_id,
                metadata={
                    "certificate_id": certificate_id,
                    "recipient_email": delivery["recipient_email"],
                },
            )

        return delivery

    @classmethod
    async def preview_email(
        cls,
        org_id: str,
        template_id: Optional[str] = None,
        certificate_id: Optional[str] = None,
        subject_override: Optional[str] = None,
        html_override: Optional[str] = None,
    ) -> Dict[str, str]:
        # 1. Resolve template
        template_doc = None
        if template_id:
            template_doc = await EmailTemplateRepository.get_by_id(template_id, org_id)
        elif not (subject_override and html_override):
            template_doc = await EmailTemplateRepository.get_default_or_first(org_id)

        if not template_doc and not (subject_override and html_override):
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
                "text_body": "",
            }

        effective_template = {
            "subject": subject_override if subject_override is not None else template_doc.get("subject", ""),
            "html_body": html_override if html_override is not None else template_doc.get("html_body", ""),
            "text_body": template_doc.get("text_body", "") if template_doc else "",
        }

        # 2. Resolve mock or real certificate data
        cert_data = {}
        recipient_data = {}
        if certificate_id:
            cert = await CertificateRepository.get_by_id(certificate_id, org_id)
            if cert:
                cert_data = cert
                recipient_data = cert.get("recipient", {})

        if not recipient_data:
            recipient_data = {
                "name": "Atul Kumar",
                "email": "atul@example.com",
            }
        if not cert_data:
            cert_data = {
                "certificate_number": "CERT-2026-000124",
                "verification_code": "V-PREVIEW-999",
                "status": "active",
                "created_at": "2026-09-28T10:00:00Z",
                "data": {
                    "program_name": "Full Stack Mastery",
                    "course_name": "Full Stack Mastery",
                }
            }

        org = await OrganizationRepository.get_by_id(org_id) or {"name": "Acme Institute", "website": "https://example.com"}

        verification_url = f"{settings.BASE_URL}/verify/{cert_data.get('verification_code', 'preview')}"
        download_url = f"{settings.BASE_URL}/api/v1/certificates/preview/download?token=sample_preview"

        return EmailRenderService.render_email(
            template_doc=effective_template,
            recipient_data=recipient_data,
            certificate_data=cert_data,
            organization_data=org,
            verification_url=verification_url,
            download_url=download_url,
        )

    @classmethod
    async def send_test_email(
        cls,
        org_id: str,
        recipient_email: str,
        template_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Preview output with test data
        preview = await cls.preview_email(org_id=org_id, template_id=template_id)

        # Settings
        email_settings_doc = await EmailSettingsRepository.get_by_org(org_id)
        provider = get_email_provider(email_settings_doc)
        sender_name = (email_settings_doc or {}).get("sender_name") or settings.DEFAULT_SENDER_NAME
        sender_email = (email_settings_doc or {}).get("sender_email") or settings.DEFAULT_SENDER_EMAIL

        msg = EmailMessage(
            to_email=recipient_email,
            to_name="Test Recipient",
            from_name=sender_name,
            from_email=sender_email,
            reply_to=(email_settings_doc or {}).get("reply_to"),
            subject=f"[TEST] {preview['subject']}",
            html_content=preview["html"],
            text_content=preview["text"],
            headers={"X-Test-Email": "true"},
        )

        res = await provider.send_email(msg)
        if user_id:
            await AuditLogRepository.log_event(
                action="email.test_sent",
                resource_type="email_test",
                resource_id=res.message_id or "test",
                organization_id=org_id,
                user_id=user_id,
                metadata={"recipient_email": recipient_email, "success": res.success},
            )

        return {
            "success": res.success,
            "message_id": res.message_id,
            "provider": res.provider,
            "error_message": res.error_message,
        }
