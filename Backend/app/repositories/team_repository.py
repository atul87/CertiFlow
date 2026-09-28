"""
Repository for teams and team_members collections (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class TeamRepository:
    @staticmethod
    def _teams():
        return DatabaseManager.get_collection("teams")

    @staticmethod
    def _members():
        return DatabaseManager.get_collection("team_members")

    @classmethod
    async def create_team(
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
            "created_by": ObjectId(created_by) if created_by else None,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._teams().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize_team(doc)

    @classmethod
    async def get_team_by_id(cls, team_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(team_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._teams().find_one({"_id": tid, "organization_id": oid})
        if not doc:
            return None
        s = cls._serialize_team(doc)
        s["member_count"] = await cls._members().count_documents({"team_id": tid})
        return s

    @classmethod
    async def get_team_by_name(cls, org_id: str, name: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._teams().find_one({"organization_id": oid, "name": name.strip()})
        return cls._serialize_team(doc) if doc else None

    @classmethod
    async def list_teams(cls, org_id: str) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._teams().find({"organization_id": oid}).sort("name", 1)
        docs = await cursor.to_list(length=100)
        results = []
        for d in docs:
            sd = cls._serialize_team(d)
            sd["member_count"] = await cls._members().count_documents({"team_id": d["_id"]})
            results.append(sd)
        return results

    @classmethod
    async def update_team(cls, team_id: str, org_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(team_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._teams().find_one_and_update(
            {"_id": tid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        if not doc:
            return None
        s = cls._serialize_team(doc)
        s["member_count"] = await cls._members().count_documents({"team_id": tid})
        return s

    @classmethod
    async def delete_team(cls, team_id: str, org_id: str) -> bool:
        try:
            tid = ObjectId(team_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        # Remove members first
        await cls._members().delete_many({"team_id": tid})
        res = await cls._teams().delete_one({"_id": tid, "organization_id": oid})
        return res.deleted_count > 0

    @classmethod
    async def add_team_member(cls, team_id: str, user_id: str, org_id: str, role: str = "member") -> Dict[str, Any]:
        tid = ObjectId(team_id)
        uid = ObjectId(user_id)
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        set_on_insert = {
            "team_id": tid,
            "user_id": uid,
            "organization_id": oid,
            "created_at": now,
        }
        res = await cls._members().find_one_and_update(
            {"team_id": tid, "user_id": uid},
            {"$set": {"role": role, "updated_at": now}, "$setOnInsert": set_on_insert},
            upsert=True,
            return_document=True,
        )
        return cls._serialize_member(res)

    @classmethod
    async def remove_team_member(cls, team_id: str, user_id: str, org_id: str) -> bool:
        try:
            tid = ObjectId(team_id)
            uid = ObjectId(user_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        res = await cls._members().delete_one({"team_id": tid, "user_id": uid, "organization_id": oid})
        return res.deleted_count > 0

    @classmethod
    async def list_team_members(cls, team_id: str, org_id: str) -> List[Dict[str, Any]]:
        try:
            tid = ObjectId(team_id)
            oid = ObjectId(org_id)
        except Exception:
            return []
        cursor = cls._members().find({"team_id": tid, "organization_id": oid})
        docs = await cursor.to_list(length=100)
        user_col = DatabaseManager.get_collection("users")
        results = []
        for d in docs:
            sd = cls._serialize_member(d)
            u = await user_col.find_one({"_id": d["user_id"]})
            if u:
                sd["user"] = {
                    "id": str(u["_id"]),
                    "name": u.get("name", ""),
                    "email": u.get("email", ""),
                }
            results.append(sd)
        return results

    @staticmethod
    def _serialize_team(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("created_by"):
            s["created_by"] = str(s["created_by"])
        return s

    @staticmethod
    def _serialize_member(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("team_id"):
            s["team_id"] = str(s["team_id"])
        if s.get("user_id"):
            s["user_id"] = str(s["user_id"])
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        return s
