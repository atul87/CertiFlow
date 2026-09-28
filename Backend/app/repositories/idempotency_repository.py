"""
Repository for idempotency_keys collection (P8).
Guarantees at-most-once execution for mutating API requests.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId

from app.core.database import DatabaseManager
from app.core.config import settings
from app.repositories.user_repository import serialize_doc


class IdempotencyRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("idempotency_keys")

    @classmethod
    async def get_key(
        cls,
        org_id: str,
        endpoint: str,
        key: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({
            "organization_id": oid,
            "endpoint": endpoint,
            "key": key.strip(),
        })
        return serialize_doc(doc) if doc else None

    @classmethod
    async def save_key(
        cls,
        org_id: str,
        endpoint: str,
        key: str,
        request_hash: str,
        response_status: int,
        response_body: Dict[str, Any],
        resource_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=settings.IDEMPOTENCY_TTL_SECONDS)
        doc = {
            "organization_id": oid,
            "endpoint": endpoint,
            "key": key.strip(),
            "request_hash": request_hash,
            "response_status": response_status,
            "response_body": response_body,
            "resource_id": resource_id,
            "created_at": now,
            "expires_at": expires_at,
        }
        res = await cls._collection().find_one_and_update(
            {"organization_id": oid, "endpoint": endpoint, "key": key.strip()},
            {"$set": doc},
            upsert=True,
            return_document=True,
        )
        return serialize_doc(res)
