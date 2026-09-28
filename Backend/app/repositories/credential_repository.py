from __future__ import annotations
import secrets
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.core.config import settings


class CredentialRepository:
    COLLECTION_NAME = "credentials"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def create(
        cls,
        organization_id: str,
        certificate_id: str,
        certificate_number: str,
        verification_code: str,
        issuer_id: str,
        achievement_id: str,
        recipient_name: str,
        recipient_email: str,
        valid_from: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        signature_algorithm: str = "Ed25519",
        key_id: str = "default_key",
        proof: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        status: str = "active"
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        credential_id = f"cred_{secrets.token_hex(12)}"
        base_url = settings.APP_BASE_URL.rstrip("/")
        credential_url = f"{base_url}/api/v1/public/credentials/{credential_id}"
        verification_url = f"{base_url}/api/v1/public/credentials/{credential_id}/verify"
        badge_url = f"{base_url}/api/v1/public/credentials/{credential_id}/badge"
        vc_url = f"{base_url}/api/v1/public/credentials/{credential_id}/vc"

        doc = {
            "credential_id": credential_id,
            "organization_id": str(organization_id),
            "certificate_id": str(certificate_id),
            "certificate_number": certificate_number,
            "verification_code": verification_code,
            "issuer_id": issuer_id,
            "achievement_id": achievement_id,
            "status": status.lower(),
            "recipient_name": recipient_name.strip(),
            "recipient_email": recipient_email.lower().strip(),
            "valid_from": valid_from or now,
            "expires_at": expires_at,
            "credential_url": credential_url,
            "verification_url": verification_url,
            "badge_url": badge_url,
            "vc_url": vc_url,
            "signature_algorithm": signature_algorithm,
            "key_id": key_id,
            "proof": proof,
            "evidence": evidence or [],
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        if "_id" in doc:
            del doc["_id"]
        return doc

    @classmethod
    async def get_by_credential_id(cls, credential_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"credential_id": credential_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_certificate_id(cls, certificate_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"certificate_id": str(certificate_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_verification_code(cls, verification_code: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"verification_code": verification_code.strip()})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def get_by_id(cls, identifier: str, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "$or": [
                {"credential_id": identifier},
                {"_id": ObjectId(identifier) if ObjectId.is_valid(identifier) else identifier}
            ]
        }
        if organization_id:
            query["organization_id"] = str(organization_id)

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def list_credentials(
        cls,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        achievement_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        query: Dict[str, Any] = {"organization_id": str(organization_id)}
        if status:
            query["status"] = status.lower()
        if achievement_id:
            query["achievement_id"] = achievement_id

        total = await cls._collection().count_documents(query)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        for it in items:
            it["id"] = str(it.pop("_id"))
        return items, total

    @classmethod
    async def update_status(
        cls,
        credential_id: str,
        status: str,
        revocation_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {
            "status": status.lower(),
            "updated_at": now
        }
        if revocation_reason:
            updates["revocation_reason"] = revocation_reason

        res = await cls._collection().find_one_and_update(
            {"credential_id": credential_id},
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        res["id"] = str(res.pop("_id"))
        return res

    @classmethod
    async def attach_proof(cls, credential_id: str, proof: Dict[str, Any]) -> None:
        await cls._collection().update_one(
            {"credential_id": credential_id},
            {"$set": {"proof": proof, "updated_at": datetime.now(timezone.utc)}}
        )
