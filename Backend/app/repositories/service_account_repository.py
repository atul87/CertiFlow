"""
Repository for service_accounts collection (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class ServiceAccountRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("service_accounts")

    @classmethod
    async def create(
        cls,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "name": name.strip(),
            "description": description,
            "status": "active",  # active, disabled
            "created_by": ObjectId(created_by) if created_by else None,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(cls, sa_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            sid = ObjectId(sa_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": sid, "organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_by_name(cls, org_id: str, name: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"organization_id": oid, "name": name.strip()})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_by_org(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._collection().find({"organization_id": oid}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        api_keys_col = DatabaseManager.get_collection("api_keys")
        results = []
        for d in docs:
            sd = cls._serialize(d)
            sd["api_keys_count"] = await api_keys_col.count_documents({
                "service_account_id": d["_id"],
                "status": "active"
            })
            results.append(sd)
        return results

    @classmethod
    async def update(cls, sa_id: str, org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            sid = ObjectId(sa_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": sid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def delete(cls, sa_id: str, org_id: str) -> bool:
        try:
            sid = ObjectId(sa_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        # Revoke associated API keys
        api_keys_col = DatabaseManager.get_collection("api_keys")
        await api_keys_col.update_many(
            {"service_account_id": sid, "organization_id": oid},
            {"$set": {"status": "revoked", "revoked_at": datetime.now(timezone.utc)}}
        )
        res = await cls._collection().delete_one({"_id": sid, "organization_id": oid})
        return res.deleted_count > 0

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("created_by"):
            s["created_by"] = str(s["created_by"])
        return s
