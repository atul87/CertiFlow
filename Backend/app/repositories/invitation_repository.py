"""
Repository for organization_invitations collection (P8).
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId

from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class InvitationRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("organization_invitations")

    @classmethod
    async def create(
        cls,
        org_id: str,
        email: str,
        role: str,
        invited_by: str,
        token_hash: str,
        expires_at: datetime,
    ) -> Dict[str, Any]:
        oid = ObjectId(org_id)
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": oid,
            "email": email.strip().lower(),
            "role": role,
            "invited_by": ObjectId(invited_by) if invited_by else None,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "status": "pending",  # pending, accepted, cancelled, expired
            "created_at": now,
            "accepted_at": None,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(cls, invitation_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(invitation_id)
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": iid, "organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_by_token_hash(cls, token_hash: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"token_hash": token_hash})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def get_pending_by_email(cls, org_id: str, email: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({
            "organization_id": oid,
            "email": email.strip().lower(),
            "status": "pending",
        })
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_invitations(cls, org_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(org_id)
        except Exception:
            return []
        query: Dict[str, Any] = {"organization_id": oid}
        if status:
            query["status"] = status
        cursor = cls._collection().find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [cls._serialize(d) for d in docs]

    @classmethod
    async def update_status(
        cls,
        invitation_id: str,
        status: str,
        accepted_at: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(invitation_id)
        except Exception:
            return None
        updates: Dict[str, Any] = {"status": status}
        if accepted_at:
            updates["accepted_at"] = accepted_at
        doc = await cls._collection().find_one_and_update(
            {"_id": iid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def delete(cls, invitation_id: str, org_id: str) -> bool:
        try:
            iid = ObjectId(invitation_id)
            oid = ObjectId(org_id)
        except Exception:
            return False
        res = await cls._collection().delete_one({"_id": iid, "organization_id": oid})
        return res.deleted_count > 0

    @staticmethod
    def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        if s.get("organization_id"):
            s["organization_id"] = str(s["organization_id"])
        if s.get("invited_by"):
            s["invited_by"] = str(s["invited_by"])
        return s
