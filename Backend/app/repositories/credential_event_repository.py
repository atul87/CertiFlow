from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.core.database import DatabaseManager


class CredentialEventRepository:
    COLLECTION_NAME = "credential_events"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def record_event(
        cls,
        credential_id: str,
        event_type: str,
        organization_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "credential_id": credential_id,
            "event_type": event_type,
            "organization_id": str(organization_id) if organization_id else None,
            "actor_id": str(actor_id) if actor_id else None,
            "metadata": metadata or {},
            "created_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        if "_id" in doc:
            del doc["_id"]
        return doc

    @classmethod
    async def list_events(cls, credential_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls._collection().find({"credential_id": credential_id}).sort("created_at", -1).limit(limit)
        items = await cursor.to_list(length=limit)
        for it in items:
            it["id"] = str(it.pop("_id"))
        return items
