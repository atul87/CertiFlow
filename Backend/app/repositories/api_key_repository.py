"""
Repository for api_keys collection (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class APIKeyRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("api_keys")

    @classmethod
    async def create(
        cls,
        org_id: str,
        name: str,
        key_hash: str,
        prefix: str,
        scopes: List[str],
        created_by: str,
        service_account_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "name": name.strip(),
            "key_hash": key_hash,
            "prefix": prefix,
            "scopes": sorted(list(set(scopes))),
            "status": "active",  # active, revoked
            "service_account_id": ObjectId(service_account_id) if service_account_id else None,
            "created_by": ObjectId(created_by) if created_by else None,
            "last_used_at": None,
            "expires_at": expires_at,
            "revoked_at": None,
            "created_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_hash(cls, key_hash: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"key_hash": key_hash})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_by_id(cls, key_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            kid = ObjectId(key_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": kid, "organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_by_org(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._collection().find({"organization_id": oid}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [cls._serialize(d) for d in docs]

    @classmethod
    async def update_last_used(cls, key_id: str) -> None:
        try:
            kid = ObjectId(key_id)
        except Exception:
            return
        await cls._collection().update_one(
            {"_id": kid},
            {"$set": {"last_used_at": datetime.now(timezone.utc)}}
        )

    @classmethod
    async def revoke(cls, key_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            kid = ObjectId(key_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": kid, "organization_id": oid},
            {"$set": {"status": "revoked", "revoked_at": now}},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def delete(cls, key_id: str, org_id: str) -> bool:
        try:
            kid = ObjectId(key_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        res = await cls._collection().delete_one({"_id": kid, "organization_id": oid})
        return res.deleted_count > 0

    @classmethod
    async def count_by_service_account(cls, sa_id: str) -> int:
        try:
            sid = ObjectId(sa_id)
        except Exception:
            return 0
        return await cls._collection().count_documents({"service_account_id": sid, "status": "active"})

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("service_account_id"):
            s["service_account_id"] = str(s["service_account_id"])
        if s.get("created_by"):
            s["created_by"] = str(s["created_by"])
        # Never expose key_hash in serialized responses
        s.pop("key_hash", None)
        return s
