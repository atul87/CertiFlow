from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.core.config import settings


class OpenBadgesV3Serializer:
    """
    Serializes a CertiFlow canonical Credential domain object into an
    1EdTech / IMS Global / W3C Open Badges 3.0 compliant JSON-LD document.
    """

    @classmethod
    def serialize(
        cls,
        credential: Dict[str, Any],
        issuer: Dict[str, Any],
        achievement: Dict[str, Any],
        evidence_items: Optional[List[Dict[str, Any]]] = None,
        proof: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        cred_id = credential["credential_id"]
        base_url = settings.APP_BASE_URL.rstrip("/")
        cred_url = f"{base_url}/api/v1/public/credentials/{cred_id}"
        issuer_id_url = f"{base_url}/api/v1/public/issuers/{issuer.get('issuer_id', 'default')}"
        achievement_id_url = f"{base_url}/api/v1/achievements/{achievement.get('achievement_id', 'default')}"

        valid_from = credential.get("valid_from")
        if isinstance(valid_from, datetime):
            valid_from_str = valid_from.astimezone(timezone.utc).isoformat()
        else:
            valid_from_str = str(valid_from or datetime.now(timezone.utc).isoformat())

        valid_until_str = None
        valid_until = credential.get("expires_at")
        if valid_until:
            if isinstance(valid_until, datetime):
                valid_until_str = valid_until.astimezone(timezone.utc).isoformat()
            else:
                valid_until_str = str(valid_until)

        # Build evidence block
        evidence_list = []
        for ev in (evidence_items or []):
            if ev.get("is_public", True):
                evidence_list.append({
                    "id": ev.get("url") or f"{cred_url}/evidence/{ev.get('id', '1')}",
                    "type": ["Evidence"],
                    "name": ev.get("name", "Evidence"),
                    "description": ev.get("description", ""),
                    "narrative": ev.get("description", "")
                })

        doc: Dict[str, Any] = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://purl.imsglobal.org/spec/ob/v3.0/context.json"
            ],
            "id": cred_url,
            "type": ["VerifiableCredential", "OpenBadgeCredential"],
            "issuer": {
                "id": issuer_id_url,
                "type": ["Profile"],
                "name": issuer.get("name", "CertiFlow Issuer"),
                "url": issuer.get("website") or issuer_id_url,
                "email": issuer.get("email")
            },
            "validFrom": valid_from_str,
            "credentialSubject": {
                "id": f"urn:uuid:{cred_id}",
                "type": ["AchievementSubject"],
                "name": credential.get("recipient_name", ""),
                "achievement": {
                    "id": achievement_id_url,
                    "type": ["Achievement"],
                    "name": achievement.get("name", "Achievement"),
                    "description": achievement.get("description", ""),
                    "criteria": {
                        "narrative": achievement.get("criteria", "Completion of required syllabus and evaluation.")
                    },
                    "tag": achievement.get("skills", []),
                    "image": {
                        "id": achievement.get("image") or f"{base_url}/images/badge-default.png",
                        "type": "Image"
                    }
                }
            }
        }

        if valid_until_str:
            doc["validUntil"] = valid_until_str

        if evidence_list:
            doc["evidence"] = evidence_list

        if proof:
            doc["proof"] = proof

        return doc
