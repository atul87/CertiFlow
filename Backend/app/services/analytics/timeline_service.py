from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.core.exceptions import NotFoundError
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.email_delivery_repository import EmailDeliveryRepository
from app.repositories.email_event_repository import EmailEventRepository


class CertificateTimelineService:
    @classmethod
    async def build_timeline(cls, certificate_id: str, org_id: str) -> Dict[str, Any]:
        """
        Aggregate certificate lifecycle events from certificate, audit logs,
        email events, and verification events into a single unified chronological timeline.
        """
        cert = await CertificateRepository.get_by_id(certificate_id, org_id)
        if not cert:
            raise NotFoundError(message="Certificate not found", code="CERTIFICATE_NOT_FOUND")

        db = DatabaseManager.get_db()
        events: List[Dict[str, Any]] = []

        # 1. Generation Event
        events.append({
            "type": "generated",
            "title": "Certificate Generated",
            "description": f"Certificate #{cert.get('certificate_number')} generated for {cert.get('recipient', {}).get('name')}",
            "timestamp": cert.get("created_at"),
            "actor": "System",
            "metadata": {
                "certificate_number": cert.get("certificate_number"),
                "verification_code": cert.get("verification_code"),
            }
        })

        # 2. Revocation Event (if applicable)
        if cert.get("status") == "revoked":
            events.append({
                "type": "revoked",
                "title": "Certificate Revoked",
                "description": f"Certificate revoked: {cert.get('revocation_reason') or 'No reason provided'}",
                "timestamp": cert.get("revoked_at") or cert.get("updated_at"),
                "actor": str(cert.get("revocation", {}).get("revoked_by") or "Administrator"),
                "metadata": {"reason": cert.get("revocation_reason")},
            })

        # 3. Email Delivery & Provider Events
        try:
            cid = ObjectId(certificate_id)
            deliveries = await db["email_deliveries"].find({"certificate_id": cid}).to_list(length=20)
            for d in deliveries:
                deliv_id = str(d["_id"])
                events.append({
                    "type": "email.queued",
                    "title": "Email Queued",
                    "description": f"Email queued for {d.get('recipient_email')}",
                    "timestamp": d.get("queued_at") or d.get("created_at"),
                    "actor": "System",
                    "metadata": {"delivery_id": deliv_id},
                })
                if d.get("sent_at"):
                    events.append({
                        "type": "email.sent",
                        "title": "Email Sent",
                        "description": f"Email dispatched via {d.get('provider', 'provider')}",
                        "timestamp": d.get("sent_at"),
                        "actor": "Email Worker",
                        "metadata": {"provider_message_id": d.get("provider_message_id")},
                    })
                if d.get("delivered_at"):
                    events.append({
                        "type": "email.delivered",
                        "title": "Email Delivered",
                        "description": f"Email successfully delivered to {d.get('recipient_email')}",
                        "timestamp": d.get("delivered_at"),
                        "actor": "Email Provider",
                        "metadata": {},
                    })
                if d.get("bounced_at"):
                    events.append({
                        "type": "email.bounced",
                        "title": "Email Bounced",
                        "description": f"Delivery bounced: {(d.get('error') or {}).get('message', 'Bounce')}",
                        "timestamp": d.get("bounced_at"),
                        "actor": "Email Provider",
                        "metadata": {"reason": (d.get("error") or {}).get("message")},
                    })

                # Individual webhook events
                webhook_events = await EmailEventRepository.get_events_for_delivery(deliv_id)
                for we in webhook_events:
                    if we["event_type"] in ("opened", "clicked", "complained"):
                        events.append({
                            "type": f"email.{we['event_type']}",
                            "title": f"Email {we['event_type'].capitalize()}",
                            "description": f"Recipient {we['event_type']} notification recorded",
                            "timestamp": we["timestamp"],
                            "actor": "Recipient",
                            "metadata": we.get("metadata", {}),
                        })
        except Exception:
            pass

        # 4. Public Verification Events
        try:
            verif_events = await db["verification_events"].find({"certificate_id": ObjectId(certificate_id)}).sort("timestamp", 1).to_list(length=100)
            for ve in verif_events:
                res_str = ve.get('result', 'valid')
                events.append({
                    "type": f"verified_{res_str}",
                    "title": f"Certificate Verified ({res_str.upper()})",
                    "description": f"Certificate verified via public verification (Result: {res_str})",
                    "timestamp": ve.get("timestamp"),
                    "actor": "Public Verifier",
                    "metadata": {
                        "result": ve.get("result"),
                        "user_agent": ve.get("user_agent"),
                    }
                })
        except Exception:
            pass

        # 5. Audit Log Events for this Certificate
        try:
            audit_records = await db["audit_logs"].find({
                "organization_id": ObjectId(org_id),
                "resource_id": ObjectId(certificate_id),
            }).to_list(length=50)
            for ar in audit_records:
                action = ar.get("action", "")
                if action not in ("certificate.generated", "certificate.revoked"):
                    events.append({
                        "type": f"audit.{action}",
                        "title": action.replace(".", " ").title(),
                        "description": f"Audit action {action} recorded",
                        "timestamp": ar.get("created_at"),
                        "actor": str(ar.get("user_id") or "User"),
                        "metadata": ar.get("metadata", {}),
                    })
        except Exception:
            pass

        # Sort all events chronologically (newest first or oldest first; let's do oldest first for standard timeline)
        events.sort(key=lambda x: x["timestamp"] or datetime.min.replace(tzinfo=timezone.utc))

        return {
            "certificate_id": str(cert["id"]),
            "certificate_number": cert.get("certificate_number", ""),
            "current_status": cert.get("status", "active"),
            "events": events,
        }
