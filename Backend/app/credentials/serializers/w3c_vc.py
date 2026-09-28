from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.core.config import settings


class W3CVCSerializer:
    """
    Serializes a canonical Credential domain object into a
    W3C Verifiable Credentials Data Model v2.0 compliant document.
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
        status_url = f"{base_url}/api/v1/public/credentials/{cred_id}/status"

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

        doc: Dict[str, Any] = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2"
            ],
            "id": cred_url,
            "type": [
                "VerifiableCredential",
                "CertificationCredential"
            ],
            "issuer": {
                "id": issuer_id_url,
                "name": issuer.get("name", "CertiFlow Issuer"),
                "url": issuer.get("website") or issuer_id_url
            },
            "validFrom": valid_from_str,
            "credentialSubject": {
                "id": f"urn:uuid:{cred_id}",
                "name": credential.get("recipient_name", ""),
                "hasCertification": {
                    "id": f"{base_url}/api/v1/achievements/{achievement.get('achievement_id', 'default')}",
                    "name": achievement.get("name", "Achievement"),
                    "description": achievement.get("description", ""),
                    "criteria": achievement.get("criteria", ""),
                    "competencies": achievement.get("skills", []),
                    "certificateNumber": credential.get("certificate_number")
                }
            },
            "credentialStatus": {
                "id": status_url,
                "type": "StatusList2021Entry",
                "statusPurpose": "revocation"
            }
        }

        if valid_until_str:
            doc["validUntil"] = valid_until_str

        if proof:
            doc["proof"] = proof

        return doc
