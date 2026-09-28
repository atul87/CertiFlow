from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from app.repositories.credential_repository import CredentialRepository
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.issuer_repository import IssuerRepository
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.credential_event_repository import CredentialEventRepository
from app.services.credential_issuer_service import CredentialIssuerService
from app.services.achievement_service import AchievementService
from app.services.credential_signing_service import CredentialSigningService
from app.services.credential_status_service import CredentialStatusService
from app.services.usage_service import UsageService
from app.services.webhook_service import WebhookService
from app.credentials.serializers.open_badges import OpenBadgesV3Serializer
from app.credentials.serializers.w3c_vc import W3CVCSerializer
from app.core.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class CredentialService:
    @classmethod
    async def issue_credential_for_certificate(
        cls,
        organization_id: str,
        certificate_id: str,
        achievement_id: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Issues, cryptographically signs, and registers a standards-based digital credential
        anchored to a generated certificate.
        """
        # Idempotency: return existing credential if already issued for this certificate
        existing = await CredentialRepository.get_by_certificate_id(certificate_id)
        if existing:
            return existing

        cert = await CertificateRepository.get_by_id(certificate_id, organization_id)
        if not cert:
            raise NotFoundError(message=f"Certificate '{certificate_id}' not found", code="CERTIFICATE_NOT_FOUND")

        # Resolve or auto-create Issuer Profile
        issuer = await CredentialIssuerService.get_or_create_default_issuer(organization_id)

        # Resolve or auto-derive Achievement Model
        if achievement_id:
            achievement = await AchievementService.get_achievement(achievement_id, organization_id)
        else:
            template = None
            if cert.get("template_id"):
                template = await TemplateRepository.get_by_id(str(cert["template_id"]), organization_id)
            if not template:
                template = {"name": cert.get("template_snapshot", {}).get("name", "Certificate of Achievement")}
            achievement = await AchievementService.get_or_create_from_template(organization_id, template)

        # Extract recipient identity
        recipient_info = cert.get("recipient") or {}
        cert_data = cert.get("data") or {}
        recipient_name = recipient_info.get("name") or cert_data.get("recipient_name") or cert_data.get("name", "Recipient")
        recipient_email = recipient_info.get("email") or cert_data.get("recipient_email") or cert_data.get("email", "recipient@example.com")

        # Create credential record
        cred = await CredentialRepository.create(
            organization_id=organization_id,
            certificate_id=certificate_id,
            certificate_number=cert.get("certificate_number", ""),
            verification_code=cert.get("verification_code", ""),
            issuer_id=issuer["issuer_id"],
            achievement_id=achievement["achievement_id"],
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            valid_from=valid_from or cert.get("issued_at") or datetime.now(timezone.utc),
            expires_at=expires_at,
            signature_algorithm="Ed25519",
            key_id=issuer["active_key_id"],
            evidence=evidence or [],
            status="active"
        )

        # Cryptographically sign the credential
        proof = await CredentialSigningService.sign_credential(cred, issuer, achievement)
        cred["proof"] = proof

        # Set initial status in dedicated status registry
        await CredentialStatusService.set_status(
            credential_id=cred["credential_id"],
            status="active",
            reason="Initial credential issuance",
            actor_id=actor_id,
            organization_id=organization_id
        )

        # Meter usage: record 'credentials_issued'
        try:
            await UsageService.record_usage(
                org_id=organization_id,
                metric="credentials_issued",
                quantity=1,
                resource_id=cred["credential_id"],
                metadata={"certificate_id": certificate_id}
            )
        except Exception as e:
            logger.warning("Failed to record usage for credential %s: %s", cred["credential_id"], e)

        # Dispatch webhook event
        try:
            await WebhookService.dispatch_event(
                org_id=organization_id,
                event_type="credential.issued",
                data={
                    "credential_id": cred["credential_id"],
                    "certificate_id": certificate_id,
                    "recipient_name": recipient_name,
                    "credential_url": cred["credential_url"],
                    "issued_at": cred["valid_from"].isoformat() if isinstance(cred["valid_from"], datetime) else str(cred["valid_from"])
                }
            )
        except Exception as e:
            logger.warning("Failed to dispatch webhook for credential %s: %s", cred["credential_id"], e)

        return cred

    @classmethod
    async def get_credential_by_id(cls, identifier: str, organization_id: Optional[str] = None) -> Dict[str, Any]:
        cred = await CredentialRepository.get_by_id(identifier, organization_id)
        if not cred:
            raise NotFoundError(message=f"Credential '{identifier}' not found", code="CREDENTIAL_NOT_FOUND")
        return cred

    @classmethod
    async def get_public_credential(cls, credential_id: str) -> Dict[str, Any]:
        """
        Privacy-safe public view.
        Omits recipient email, internal database IDs, and sensitive evidence.
        """
        cred = await CredentialRepository.get_by_credential_id(credential_id)
        if not cred:
            raise NotFoundError(message=f"Credential '{credential_id}' not found", code="CREDENTIAL_NOT_FOUND")

        issuer = await IssuerRepository.get_by_issuer_id(cred["issuer_id"])
        achievement = await AchievementRepository.get_by_id(cred["achievement_id"])

        public_evidence = [
            e for e in cred.get("evidence", [])
            if e.get("is_public", True)
        ]

        return {
            "credential_id": cred["credential_id"],
            "status": cred.get("status", "active"),
            "recipient_name": cred.get("recipient_name", ""),
            "achievement_name": achievement.get("name", "Achievement") if achievement else "Achievement",
            "achievement_description": achievement.get("description", "") if achievement else "",
            "achievement_criteria": achievement.get("criteria", "") if achievement else "",
            "achievement_skills": achievement.get("skills", []) if achievement else [],
            "issuer_name": issuer.get("name", "CertiFlow") if issuer else "CertiFlow",
            "issuer_url": issuer.get("issuer_url", "") if issuer else "",
            "issued_at": cred.get("valid_from") or cred.get("created_at"),
            "expires_at": cred.get("expires_at"),
            "credential_url": cred["credential_url"],
            "verification_url": cred["verification_url"],
            "badge_url": cred["badge_url"],
            "vc_url": cred["vc_url"],
            "evidence": public_evidence
        }

    @classmethod
    async def get_open_badge_json(cls, credential_id: str) -> Dict[str, Any]:
        cred = await CredentialRepository.get_by_credential_id(credential_id)
        if not cred:
            raise NotFoundError(message=f"Credential '{credential_id}' not found", code="CREDENTIAL_NOT_FOUND")

        issuer = await IssuerRepository.get_by_issuer_id(cred["issuer_id"])
        if not issuer:
            raise NotFoundError(message="Issuer not found", code="ISSUER_NOT_FOUND")

        achievement = await AchievementRepository.get_by_id(cred["achievement_id"])
        if not achievement:
            raise NotFoundError(message="Achievement not found", code="ACHIEVEMENT_NOT_FOUND")

        return OpenBadgesV3Serializer.serialize(
            credential=cred,
            issuer=issuer,
            achievement=achievement,
            evidence_items=cred.get("evidence"),
            proof=cred.get("proof")
        )

    @classmethod
    async def get_w3c_vc_json(cls, credential_id: str) -> Dict[str, Any]:
        cred = await CredentialRepository.get_by_credential_id(credential_id)
        if not cred:
            raise NotFoundError(message=f"Credential '{credential_id}' not found", code="CREDENTIAL_NOT_FOUND")

        issuer = await IssuerRepository.get_by_issuer_id(cred["issuer_id"])
        if not issuer:
            raise NotFoundError(message="Issuer not found", code="ISSUER_NOT_FOUND")

        achievement = await AchievementRepository.get_by_id(cred["achievement_id"])
        if not achievement:
            raise NotFoundError(message="Achievement not found", code="ACHIEVEMENT_NOT_FOUND")

        return W3CVCSerializer.serialize(
            credential=cred,
            issuer=issuer,
            achievement=achievement,
            evidence_items=cred.get("evidence"),
            proof=cred.get("proof")
        )

    @classmethod
    async def list_credentials(
        cls,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        achievement_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        return await CredentialRepository.list_credentials(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            status=status,
            achievement_id=achievement_id
        )

    @classmethod
    async def revoke_credential(
        cls,
        credential_id: str,
        organization_id: str,
        reason: str,
        actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        cred = await cls.get_credential_by_id(credential_id, organization_id)
        updated = await CredentialStatusService.set_status(
            credential_id=cred["credential_id"],
            status="revoked",
            reason=reason,
            actor_id=actor_id,
            organization_id=organization_id
        )
        try:
            await WebhookService.dispatch_event(
                org_id=organization_id,
                event_type="credential.revoked",
                data={"credential_id": cred["credential_id"], "reason": reason}
            )
        except Exception:
            pass
        return updated

    @classmethod
    async def suspend_credential(
        cls,
        credential_id: str,
        organization_id: str,
        reason: str,
        actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        cred = await cls.get_credential_by_id(credential_id, organization_id)
        updated = await CredentialStatusService.set_status(
            credential_id=cred["credential_id"],
            status="suspended",
            reason=reason,
            actor_id=actor_id,
            organization_id=organization_id
        )
        try:
            await WebhookService.dispatch_event(
                org_id=organization_id,
                event_type="credential.suspended",
                data={"credential_id": cred["credential_id"], "reason": reason}
            )
        except Exception:
            pass
        return updated

    @classmethod
    async def restore_credential(
        cls,
        credential_id: str,
        organization_id: str,
        actor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        cred = await cls.get_credential_by_id(credential_id, organization_id)
        updated = await CredentialStatusService.set_status(
            credential_id=cred["credential_id"],
            status="active",
            reason="Restored by authority",
            actor_id=actor_id,
            organization_id=organization_id
        )
        try:
            await WebhookService.dispatch_event(
                org_id=organization_id,
                event_type="credential.restored",
                data={"credential_id": cred["credential_id"]}
            )
        except Exception:
            pass
        return updated
