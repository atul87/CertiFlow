from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from pymongo import ReturnDocument
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailDeliveryRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_deliveries")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        for field in ("organization_id", "certificate_id", "issuance_job_id", "email_job_id", "template_id"):
            if doc.get(field):
                s[field] = str(doc[field])
        return s

    @classmethod
    async def create(
        cls,
        organization_id: str,
        certificate_id: str,
        recipient_email: str,
        recipient_name: str,
        template_id: Optional[str] = None,
        delivery_mode: str = "link",
        provider: str = "mock",
        issuance_job_id: Optional[str] = None,
        email_job_id: Optional[str] = None,
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "certificate_id": ObjectId(certificate_id),
            "issuance_job_id": ObjectId(issuance_job_id) if issuance_job_id else None,
            "email_job_id": ObjectId(email_job_id) if email_job_id else None,
            "recipient_email": recipient_email.strip().lower(),
            "recipient_name": recipient_name.strip(),
            "template_id": ObjectId(template_id) if template_id else None,
            "provider": provider,
            "delivery_mode": delivery_mode,
            "status": "queued",
            "attempts": 0,
            "max_attempts": max_attempts,
            "provider_message_id": None,
            "error": None,
            "queued_at": now,
            "sending_at": None,
            "sent_at": None,
            "delivered_at": None,
            "failed_at": None,
            "bounced_at": None,
            "complained_at": None,
            "next_retry_at": None,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(
        cls,
        delivery_id: str,
        organization_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        query: Dict[str, Any] = {"_id": did}
        if organization_id:
            try:
                query["organization_id"] = ObjectId(organization_id)
            except Exception:
                return None
        doc = await cls._collection().find_one(query)
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_by_provider_message_id(cls, provider_message_id: str) -> Optional[Dict[str, Any]]:
        if not provider_message_id:
            return None
        doc = await cls._collection().find_one({"provider_message_id": provider_message_id})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_latest_for_certificate(cls, certificate_id: str) -> Optional[Dict[str, Any]]:
        try:
            cid = ObjectId(certificate_id)
        except Exception:
            return None
        doc = await cls._collection().find_one(
            {"certificate_id": cid},
            sort=[("created_at", -1)]
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_deliveries(
        cls,
        organization_id: str,
        certificate_id: Optional[str] = None,
        email_job_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0
        query: Dict[str, Any] = {"organization_id": oid}
        if certificate_id:
            try:
                query["certificate_id"] = ObjectId(certificate_id)
            except Exception:
                return [], 0
        if email_job_id:
            try:
                query["email_job_id"] = ObjectId(email_job_id)
            except Exception:
                return [], 0
        if status:
            query["status"] = status

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        return [cls._serialize(d) for d in items], total

    @classmethod
    async def claim_for_sending(cls, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Atomically transition from queued or failed -> sending and increment attempts."""
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {
                "_id": did,
                "status": {"$in": ["queued", "failed"]},
                "$expr": {"$lt": ["$attempts", "$max_attempts"]},
            },
            {
                "$set": {
                    "status": "sending",
                    "sending_at": now,
                    "updated_at": now,
                },
                "$inc": {"attempts": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def mark_sent(
        cls,
        delivery_id: str,
        provider_message_id: str,
        provider: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "sent",
                    "provider_message_id": provider_message_id,
                    "provider": provider,
                    "sent_at": now,
                    "error": None,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def mark_failed(
        cls,
        delivery_id: str,
        error_code: str,
        message: str,
        retryable: bool,
        next_retry_at: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "failed",
                    "failed_at": now,
                    "error": {
                        "error_code": error_code,
                        "message": message,
                        "retryable": retryable,
                    },
                    "next_retry_at": next_retry_at,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def mark_delivered(
        cls,
        delivery_id: str,
        timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = timestamp or datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "delivered",
                    "delivered_at": now,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def mark_bounced(
        cls,
        delivery_id: str,
        reason: str = "bounce",
        timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = timestamp or datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "bounced",
                    "bounced_at": now,
                    "error": {
                        "error_code": "EMAIL_BOUNCED",
                        "message": reason,
                        "retryable": False,
                    },
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def mark_complained(
        cls,
        delivery_id: str,
        reason: str = "complaint",
        timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = timestamp or datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "complained",
                    "complained_at": now,
                    "error": {
                        "error_code": "EMAIL_COMPLAINT",
                        "message": reason,
                        "retryable": False,
                    },
                    "updated_at": datetime.now(timezone.utc),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def reset_for_retry(cls, delivery_id: str) -> Optional[Dict[str, Any]]:
        try:
            did = ObjectId(delivery_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": did},
            {
                "$set": {
                    "status": "queued",
                    "next_retry_at": None,
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return cls._serialize(doc) if doc else None
