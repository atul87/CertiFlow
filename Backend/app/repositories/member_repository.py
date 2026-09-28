"""
Repository for organization_members collection (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class MemberRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("organization_members")

    @classmethod
    async def create_member(
        cls,
        org_id: str,
        user_id: str,
        role: str = "member",
        status: str = "active",
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        uid = ObjectId(user_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "user_id": uid,
            "role": role,
            "status": status,
            "joined_at": now if status == "active" else None,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(cls, member_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            mid = ObjectId(member_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": mid, "organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_by_user_id(cls, org_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
            uid = ObjectId(user_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"organization_id": oid, "user_id": uid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_members(
        cls,
        org_id: str,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"organization_id": oid}
        if status:
            query["status"] = status
        else:
            query["status"] = {"$ne": "removed"}

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", 1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        user_col = DatabaseManager.get_collection("users")
        results = []
        for d in docs:
            sd = cls._serialize(d)
            # Attach user details
            u = await user_col.find_one({"_id": d["user_id"]})
            if u:
                sd["user"] = {
                    "id": str(u["_id"]),
                    "name": u.get("name", ""),
                    "email": u.get("email", ""),
                }
            results.append(sd)

        return results, total

    @classmethod
    async def update_member(
        cls,
        member_id: str,
        org_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        try:
            mid = ObjectId(member_id)
            oid = ObjectId(org_id)
        except Exception:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": mid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def count_owners(cls, org_id: str) -> int:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return 0
        return await cls._collection().count_documents({
            "organization_id": oid,
            "role": "owner",
            "status": "active",
        })

    @classmethod
    async def count_members_with_role(cls, org_id: str, role_name: str) -> int:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return 0
        return await cls._collection().count_documents({
            "organization_id": oid,
            "role": role_name,
            "status": {"$ne": "removed"},
        })

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("user_id"):
            s["user_id"] = str(s["user_id"])
        return s
