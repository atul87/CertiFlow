"""
Outbox Repository — P12.22 & P12.23.
Manages transactional outbox events with exponential backoff and dead-letter handling.
"""
from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClientSession
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)


def _serialize_outbox(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    d = dict(doc)
    d["id"] = str(d.pop("_id"))
    if "organization_id" in d and isinstance(d["organization_id"], ObjectId):
        d["organization_id"] = str(d["organization_id"])
    return d


class OutboxRepository:
    @classmethod
    def _collection(cls) -> AsyncIOMotorCollection:
        return DatabaseManager.get_collection("outbox_events")

    @classmethod
    async def create_event(
        cls,
        org_id: str,
        event_type: str,
        destination_type: str,
        payload: Dict[str, Any],
        max_attempts: int = 3,
        session: Optional[AsyncIOMotorClientSession] = None,
    ) -> Dict[str, Any]:
        """Insert an outbox event, optionally inside a MongoDB ACID transaction."""
        now = datetime.now(timezone.utc)
        event_id = f"outbox_{uuid.uuid4().hex[:16]}"
        doc = {
            "event_id": event_id,
            "organization_id": ObjectId(org_id) if org_id else None,
            "event_type": event_type,
            "destination_type": destination_type,  # 'webhook' or 'email'
            "payload": payload,
            "status": "pending",
            "attempts": 0,
            "max_attempts": max_attempts,
            "next_attempt_at": now,
            "last_error": None,
            "created_at": now,
            "delivered_at": None,
        }
        res = await cls._collection().insert_one(doc, session=session)
        doc["_id"] = res.inserted_id
        return _serialize_outbox(doc)

    @classmethod
    async def claim_pending_events(cls, batch_size: int = 20) -> List[Dict[str, Any]]:
        """Atomically claim pending events ready for dispatch."""
        now = datetime.now(timezone.utc)
        claimed = []
        cursor = cls._collection().find({
            "status": {"$in": ["pending", "retrying"]},
            "next_attempt_at": {"$lte": now}
        }).limit(batch_size)

        candidate_ids = [doc["_id"] async for doc in cursor]
        if not candidate_ids:
            return []

        await cls._collection().update_many(
            {"_id": {"$in": candidate_ids}},
            {"$set": {"status": "processing"}}
        )

        cursor_claimed = cls._collection().find({"_id": {"$in": candidate_ids}})
        async for doc in cursor_claimed:
            claimed.append(_serialize_outbox(doc))
        return claimed

    @classmethod
    async def mark_delivered(cls, event_id: str) -> None:
        """Mark an outbox event as successfully delivered."""
        now = datetime.now(timezone.utc)
        await cls._collection().update_one(
            {"event_id": event_id},
            {
                "$set": {
                    "status": "delivered",
                    "delivered_at": now,
                    "last_error": None,
                }
            }
        )

    @classmethod
    async def record_failure(
        cls,
        event_id: str,
        error_message: str,
        backoff_seconds: int = 15,
    ) -> str:
        """
        Record delivery failure with exponential backoff or dead-letter transition.
        Returns final status ('retrying' or 'dead_letter').
        """
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one({"event_id": event_id})
        if not doc:
            return "unknown"

        attempts = doc.get("attempts", 0) + 1
        max_attempts = doc.get("max_attempts", 3)

        if attempts >= max_attempts:
            status = "dead_letter"
            next_attempt = None
            logger.error("Outbox event %s dead-lettered after %d attempts: %s", event_id, attempts, error_message)
        else:
            status = "retrying"
            next_attempt = now + timedelta(seconds=backoff_seconds)
            logger.warning("Outbox event %s failed (attempt %d/%d), retrying in %ds: %s", event_id, attempts, max_attempts, backoff_seconds, error_message)

        await cls._collection().update_one(
            {"event_id": event_id},
            {
                "$set": {
                    "status": status,
                    "attempts": attempts,
                    "last_error": str(error_message)[:500],
                    "next_attempt_at": next_attempt,
                }
            }
        )
        return status

    @classmethod
    async def list_dead_letters(cls, org_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"status": "dead_letter"}
        if org_id:
            try:
                query["organization_id"] = ObjectId(org_id)
            except Exception:
                pass
        cursor = cls._collection().find(query).sort("created_at", -1).limit(limit)
        return [_serialize_outbox(doc) async for doc in cursor]
