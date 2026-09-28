"""
Repository for webhook_endpoints, webhook_events, and webhook_deliveries collections (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class WebhookRepository:
    @staticmethod
    def _endpoints():
        return DatabaseManager.get_collection("webhook_endpoints")

    @staticmethod
    def _events():
        return DatabaseManager.get_collection("webhook_events")

    @staticmethod
    def _deliveries():
        return DatabaseManager.get_collection("webhook_deliveries")

    # ---------------------------------------------------------------------------
    # Webhook Endpoints
    # ---------------------------------------------------------------------------

    @classmethod
    async def create_endpoint(
        cls,
        org_id: str,
        url: str,
        events: List[str],
        secret_hash: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "url": url.strip(),
            "events": sorted(list(set(events))),
            "secret_hash": secret_hash,
            "description": description,
            "status": "active",  # active, disabled
            "created_by": ObjectId(created_by) if created_by else None,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._endpoints().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize_endpoint(doc)

    @classmethod
    async def get_endpoint_by_id(cls, endpoint_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            eid = ObjectId(endpoint_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._endpoints().find_one({"_id": eid, "organization_id": oid})
        return cls._serialize_endpoint(doc) if doc else None

    @classmethod
    async def list_endpoints_by_org(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._endpoints().find({"organization_id": oid}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [cls._serialize_endpoint(d) for d in docs]

    @classmethod
    async def list_endpoints_for_event(cls, org_id: str, event_type: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._endpoints().find({
            "organization_id": oid,
            "status": "active",
            "events": {"$in": [event_type, "*"]},
        })
        docs = await cursor.to_list(length=50)
        return [cls._serialize_endpoint(d) for d in docs]

    @classmethod
    async def update_endpoint(
        cls,
        endpoint_id: str,
        org_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        try:
            eid = ObjectId(endpoint_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._endpoints().find_one_and_update(
            {"_id": eid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize_endpoint(doc) if doc else None

    @classmethod
    async def delete_endpoint(cls, endpoint_id: str, org_id: str) -> bool:
        try:
            eid = ObjectId(endpoint_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        res = await cls._endpoints().delete_one({"_id": eid, "organization_id": oid})
        return res.deleted_count > 0

    # ---------------------------------------------------------------------------
    # Webhook Events
    # ---------------------------------------------------------------------------

    @classmethod
    async def create_event(
        cls,
        event_id: str,
        org_id: str,
        event_type: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "event_id": event_id,
            "organization_id": oid,
            "event_type": event_type,
            "data": data,
            "created_at": now,
        }
        await cls._events().insert_one(doc)
        return serialize_doc(doc)

    @classmethod
    async def get_event(cls, event_id: str) -> Optional[Dict[str, Any]]:
        doc = await cls._events().find_one({"event_id": event_id})
        return serialize_doc(doc) if doc else None

    # ---------------------------------------------------------------------------
    # Webhook Deliveries
    # ---------------------------------------------------------------------------

    @classmethod
    async def create_delivery(
        cls,
        org_id: str,
        endpoint_id: str,
        event_id: str,
        event_type: str,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        eid = ObjectId(endpoint_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "webhook_endpoint_id": eid,
            "event_id": event_id,
            "event_type": event_type,
            "attempt": 1,
            "status": "queued",  # queued, sending, delivered, retrying, failed
            "http_status": None,
            "response_time_ms": None,
            "error": None,
            "next_retry_at": None,
            "created_at": now,
            "delivered_at": None,
        }
        res = await cls._deliveries().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize_delivery(doc)

    @classmethod
    async def update_delivery(
        cls,
        delivery_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        doc = await cls._deliveries().find_one_and_update(
            {"_id": did},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize_delivery(doc) if doc else None

    @classmethod
    async def get_delivery(cls, delivery_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._deliveries().find_one({"_id": did, "organization_id": oid})
        return cls._serialize_delivery(doc) if doc else None

    @classmethod
    async def list_deliveries(
        cls,
        org_id: str,
        endpoint_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return [], 0
        query: Dict[str, Any] = {"organization_id": oid}
        if endpoint_id:
            try:
                query["webhook_endpoint_id"] = ObjectId(endpoint_id)
            except Exception:
                return [], 0

        total = await cls._deliveries().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._deliveries().find(query).sort("created_at", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [cls._serialize_delivery(d) for d in docs], total

    @staticmethod
    def _serialize_endpoint(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("created_by"):
            s["created_by"] = str(s["created_by"])
        return s

    @staticmethod
    def _serialize_delivery(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("webhook_endpoint_id"):
            s["webhook_endpoint_id"] = str(s["webhook_endpoint_id"])
        return s
