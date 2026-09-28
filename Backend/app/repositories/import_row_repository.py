from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class ImportRowRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("import_rows")

    @classmethod
    async def bulk_insert(
        cls,
        import_id: str,
        organization_id: str,
        validated_rows: List[Dict[str, Any]]
    ) -> int:
        """Efficient bulk insertion of validated recipient rows."""
        now = datetime.now(timezone.utc)
        docs = []
        iid = ObjectId(import_id)
        oid = ObjectId(organization_id)

        for r in validated_rows:
            docs.append({
                "import_id": iid,
                "organization_id": oid,
                "row_number": r["row_number"],
                "raw_data": r.get("raw_data", {}),
                "data": r.get("data", {}),
                "status": r.get("status", "valid"),
                "errors": r.get("errors", []),
                "warnings": r.get("warnings", []),
                "created_at": now
            })

        if not docs:
            return 0

        # Delete any existing rows for this import (if re-validating)
        await cls._collection().delete_many({"import_id": iid})

        res = await cls._collection().insert_many(docs, ordered=False)
        return len(res.inserted_ids)

    @classmethod
    async def list_rows(
        cls,
        import_id: str,
        organization_id: str,
        page: int = 1,
        limit: int = 50,
        status: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"import_id": iid, "organization_id": oid}
        if status:
            query["status"] = status

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("row_number", 1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["import_id"] = str(doc["import_id"])
            s["organization_id"] = str(doc["organization_id"])
            results.append(s)

        return results, total

    @classmethod
    async def get_preview_rows(
        cls,
        import_id: str,
        organization_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return []

        cursor = cls._collection().find({"import_id": iid, "organization_id": oid}).sort("row_number", 1).limit(limit)
        items = await cursor.to_list(length=limit)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["import_id"] = str(doc["import_id"])
            s["organization_id"] = str(doc["organization_id"])
            results.append(s)

        return results

    @classmethod
    async def get_error_rows(
        cls,
        import_id: str,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        try:
            iid = ObjectId(import_id)
            oid = ObjectId(organization_id)
        except Exception:
            return []

        cursor = cls._collection().find({
            "import_id": iid,
            "organization_id": oid,
            "status": "error"
        }).sort("row_number", 1)
        items = await cursor.to_list(length=5000)

        results = []
        for doc in items:
            s = serialize_doc(doc)
            s["import_id"] = str(doc["import_id"])
            s["organization_id"] = str(doc["organization_id"])
            results.append(s)

        return results
