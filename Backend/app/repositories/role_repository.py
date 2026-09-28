"""
Repository for roles collection (P8).
Handles custom and system roles per organization.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class RoleRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("roles")

    @classmethod
    async def create(
        cls,
        org_id: str,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        is_system_role: bool = False,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "name": name.strip(),
            "description": description,
            "permissions": sorted(list(set(permissions))),
            "is_system_role": is_system_role,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(cls, role_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            rid = ObjectId(role_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": rid, "organization_id": oid})
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
    async def list_roles(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._collection().find({"organization_id": oid}).sort("name", 1)
        docs = await cursor.to_list(length=100)
        return [cls._serialize(d) for d in docs]

    @classmethod
    async def update(cls, role_id: str, org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            rid = ObjectId(role_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": rid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def delete(cls, role_id: str, org_id: str) -> bool:
        try:
            rid = ObjectId(role_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        res = await cls._collection().delete_one({"_id": rid, "organization_id": oid, "is_system_role": False})
        return res.deleted_count > 0

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        return s
