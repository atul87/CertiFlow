from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class ImportRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("imports")

    @classmethod
    async def create(
        cls,
        organization_id: str,
        template_id: str,
        template_version_id: Optional[str],
        filename: str,
        file_type: str,
        file_size: int,
        storage_key: str,
        created_by: str
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id),
            "template_version_id": ObjectId(template_version_id) if template_version_id else None,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "storage_key": storage_key,
            "status": "uploaded",  # uploaded, parsing, parsed, mapping_required, validated, ready, failed, cancelled
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "warning_rows": 0,
            "columns": [],
            "column_profiles": [],
            "created_by": ObjectId(created_by),
            "created_at": now,
            "updated_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["template_id"] = str(doc["template_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("template_version_id"):
            s["template_version_id"] = str(doc["template_version_id"])
        return s

    @classmethod
    async def get_by_id(cls, import_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        doc = await cls._collection().find_one({"_id": iid, "organization_id": oid})
        if not doc:
            return None
        s = serialize_doc(doc)
        s["organization_id"] = str(doc["organization_id"])
        s["template_id"] = str(doc["template_id"])
        s["created_by"] = str(doc["created_by"])
        if doc.get("template_version_id"):
            s["template_version_id"] = str(doc["template_version_id"])
        return s

    @classmethod
    async def list_imports(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"organization_id": oid}
        if status:
            query["status"] = status
        if template_id:
            try:
                query["template_id"] = ObjectId(template_id)
            except Exception:
                pass

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["organization_id"] = str(doc["organization_id"])
            s["template_id"] = str(doc["template_id"])
            s["created_by"] = str(doc["created_by"])
            if doc.get("template_version_id"):
                s["template_version_id"] = str(doc["template_version_id"])
            results.append(s)

        return results, total

    @classmethod
    async def update(
        cls,
        import_id: str,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None

        updates["updated_at"] = datetime.now(timezone.utc)
        res = await cls._collection().find_one_and_update(
            {"_id": iid, "organization_id": oid},
            {"$set": updates},
            return_document=True
        )
        if not res:
            return None
        s = serialize_doc(res)
        s["organization_id"] = str(res["organization_id"])
        s["template_id"] = str(res["template_id"])
        s["created_by"] = str(res["created_by"])
        if res.get("template_version_id"):
            s["template_version_id"] = str(res["template_version_id"])
        return s
