from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class EmailTemplateRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("email_templates")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        s["organization_id"] = str(doc.get("organization_id", ""))
        s["created_by"] = str(doc.get("created_by", ""))
        return s

    @classmethod
    async def create(
        cls,
        organization_id: str,
        name: str,
        subject: str,
        html_body: str,
        text_body: str,
        variables: List[str],
        created_by: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "name": name,
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body,
            "variables": variables,
            "status": "active",
            "created_by": ObjectId(created_by),
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls._serialize(doc)

    @classmethod
    async def get_by_id(cls, template_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": tid, "organization_id": oid})
        return cls._serialize(doc) if doc else None

    @classmethod
    async def list_templates(
        cls,
        organization_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return []
        query: Dict[str, Any] = {"organization_id": oid}
        if status:
            query["status"] = status
        cursor = cls._collection().find(query).sort("created_at", -1)
        items = await cursor.to_list(length=100)
        return [cls._serialize(doc) for doc in items]

    @classmethod
    async def update(
        cls,
        template_id: str,
        organization_id: str,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None
        updates["updated_at"] = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": tid, "organization_id": oid},
            {"$set": updates},
            return_document=True,
        )
        return cls._serialize(doc) if doc else None

    @classmethod
    async def delete(cls, template_id: str, organization_id: str) -> bool:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return False
        res = await cls._collection().delete_one({"_id": tid, "organization_id": oid})
        return res.deleted_count > 0

    @classmethod
    async def get_default_or_first(cls, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"organization_id": oid, "status": "active"}, sort=[("created_at", 1)])
        return cls._serialize(doc) if doc else None
