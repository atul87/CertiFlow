from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailSuppressionRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_suppressions")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if doc.get("organization_id"):
            s["organization_id"] = str(doc["organization_id"])
        return s

    @classmethod
    async def is_suppressed(cls, organization_id: str, email: str) -> bool:
        if not email:
            return False
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return False
        clean_email = email.strip().lower()
        doc = await cls._collection().find_one({"organization_id": oid, "email": clean_email})
        return doc is not None

    @classmethod
    async def add_suppression(
        cls,
        organization_id: str,
        email: str,
        reason: str = "hard_bounce",
    ) -> Dict[str, Any]:
        oid = ObjectId(organization_id)
        clean_email = email.strip().lower()
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"organization_id": oid, "email": clean_email},
            {
                "$set": {
                    "reason": reason,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "organization_id": oid,
                    "email": clean_email,
                    "created_at": now,
                }
            },
            upsert=True,
            return_document=True,
        )
        return cls._serialize(doc)

    @classmethod
    async def remove_suppression(cls, organization_id: str, email: str) -> bool:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return False
        clean_email = email.strip().lower()
        res = await cls._collection().delete_one({"organization_id": oid, "email": clean_email})
        return res.deleted_count > 0

    @classmethod
    async def list_suppressions(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0
        query = {"organization_id": oid}
        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [cls._serialize(d) for d in items], total
