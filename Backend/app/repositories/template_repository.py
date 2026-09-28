import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class TemplateRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("templates")

    @classmethod
    async def create(
        cls,
        organization_id: str,
        name: str,
        created_by: str,
        description: Optional[str] = ""
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "name": name.strip(),
            "description": description.strip() if description else "",
            "status": "active",
            "current_version_id": None,
            "created_by": ObjectId(created_by),
            "created_at": now,
            "updated_at": now,
            "deleted_at": None
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        return s

    @classmethod
    async def get_by_id(cls, template_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        doc = await cls._collection().find_one({
            "_id": tid,
            "organization_id": oid,
            "deleted_at": None
        })
        if not doc:
            return None
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("current_version_id"):
            s["current_version_id"] = str(doc["current_version_id"])
        return s

    @classmethod
    async def list_templates(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = "active"
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {
            "organization_id": oid,
            "deleted_at": None
        }
        if status:
            query["status"] = status

        if search and search.strip():
            pattern = re.compile(re.escape(search.strip()), re.IGNORECASE)
            query["$or"] = [
                {"name": pattern},
                {"description": pattern}
            ]

        total = await cls._collection().count_documents(query)

        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["organization_id"] = str(doc["organization_id"])
            s["created_by"] = str(doc["created_by"])
            if doc.get("current_version_id"):
                s["current_version_id"] = str(doc["current_version_id"])
            results.append(s)

        return results, total

    @classmethod
    async def update(
        cls,
        template_id: str,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": tid, "organization_id": oid, "deleted_at": None},
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["organization_id"] = str(res["organization_id"])
        s["created_by"] = str(res["created_by"])
        if res.get("current_version_id"):
            s["current_version_id"] = str(res["current_version_id"])
        return s

    @classmethod
    async def set_current_version(
        cls,
        template_id: str,
        organization_id: str,
        version_id: str
    ) -> bool:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
            vid = ObjectId(version_id)
        except Exception:
            return False

        res = await cls._collection().update_one(
            {"_id": tid, "organization_id": oid},
            {"$set": {"current_version_id": vid, "updated_at": datetime.now(timezone.utc)}}
        )
        return res.modified_count > 0

    @classmethod
    async def archive(cls, template_id: str, organization_id: str) -> bool:
        try:
            tid = ObjectId(template_id)
            oid = ObjectId(organization_id)
        except Exception:
            return False

        now = datetime.now(timezone.utc)
        res = await cls._collection().update_one(
            {"_id": tid, "organization_id": oid},
            {"$set": {"status": "archived", "deleted_at": now, "updated_at": now}}
        )
        return res.modified_count > 0
