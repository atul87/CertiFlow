from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class VerificationEventRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("verification_events")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if doc.get("certificate_id"):
            s["certificate_id"] = str(doc["certificate_id"])
        if doc.get("organization_id"):
            s["organization_id"] = str(doc["organization_id"])
        return s

    @classmethod
    async def create(
        cls,
        certificate_id: Optional[str],
        verification_code: str,
        organization_id: Optional[str],
        result: str,
        user_agent: Optional[str] = None,
        ip_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "certificate_id": ObjectId(certificate_id) if certificate_id else None,
            "verification_code": verification_code,
            "organization_id": ObjectId(organization_id) if organization_id else None,
            "result": result,  # valid, revoked, expired, not_found, invalid
            "user_agent": user_agent,
            "ip_hash": ip_hash,
            "timestamp": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def list_by_certificate(
        cls,
        certificate_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        try:
            cid = ObjectId(certificate_id)
        except Exception:
            return []

        cursor = cls._collection().find({"certificate_id": cid}).sort("timestamp", -1).limit(limit)
        items = await cursor.to_list(length=limit)
        return [cls._serialize(doc) for doc in items]

    @classmethod
    async def list_by_organization(
        cls,
        organization_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return []

        cursor = cls._collection().find({"organization_id": oid}).sort("timestamp", -1).limit(limit)
        items = await cursor.to_list(length=limit)
        return [cls._serialize(doc) for doc in items]
