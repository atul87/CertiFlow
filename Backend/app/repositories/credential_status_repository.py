from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.core.database import DatabaseManager


class CredentialStatusRepository:
    COLLECTION_NAME = "credential_status"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def set_status(
        cls,
        credential_id: str,
        status: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "credential_id": credential_id,
            "status": status.lower(),
            "reason": reason,
            "updated_at": now
        }
        res = await cls._collection().find_one_and_update(
            {"credential_id": credential_id},
            {
                "$set": doc,
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=True
        )
        res["id"] = str(res.pop("_id"))
        return res

    @classmethod
    async def get_status(cls, credential_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"credential_id": credential_id})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc
