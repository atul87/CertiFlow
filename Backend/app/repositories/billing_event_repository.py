from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from pymongo.errors import DuplicateKeyError
from app.core.database import DatabaseManager


class BillingEventRepository:
    COLLECTION_NAME = "billing_events"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def record_event(
        cls,
        provider: str,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any],
        organization_id: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Record webhook event for strict idempotency.
        Returns: (is_new, event_doc)
        If the event has already been recorded, returns (False, existing_doc).
        """
        now = datetime.now(timezone.utc)
        doc = {
            "provider": provider,
            "event_id": event_id,
            "event_type": event_type,
            "organization_id": organization_id,
            "payload": payload,
            "processed": False,
            "processed_at": None,
            "created_at": now
        }
        try:
            res = await cls._collection().insert_one(doc)
            doc["id"] = str(res.inserted_id)
            return True, doc
        except DuplicateKeyError:
            # Event already seen!
            existing = await cls._collection().find_one({"provider": provider, "event_id": event_id})
            if existing:
                existing["id"] = str(existing.pop("_id"))
            return False, existing

    @classmethod
    async def mark_processed(cls, provider: str, event_id: str) -> bool:
        """Mark event as safely processed."""
        now = datetime.now(timezone.utc)
        res = await cls._collection().update_one(
            {"provider": provider, "event_id": event_id},
            {"$set": {"processed": True, "processed_at": now}}
        )
        return res.modified_count > 0
