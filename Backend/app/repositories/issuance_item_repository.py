from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


class IssuanceItemRepository:
    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("issuance_job_items")

    @classmethod
    def _serialize(cls, doc: Dict[str, Any]) -> Dict[str, Any]:
        s = serialize_doc(doc)
        s["job_id"] = str(doc.get("job_id", ""))
        s["organization_id"] = str(doc.get("organization_id", ""))
        s["import_row_id"] = str(doc.get("import_row_id", ""))
        if doc.get("certificate_id"):
            s["certificate_id"] = str(doc.get("certificate_id"))
        return s

    @classmethod
    async def bulk_create(
        cls,
        job_id: str,
        organization_id: str,
        valid_rows: List[Dict[str, Any]],
    ) -> int:
        now = datetime.now(timezone.utc)
        jid = ObjectId(job_id)
        oid = ObjectId(organization_id)

        docs = []
        for r in valid_rows:
            row_data = r.get("data", {})
            # Extract recipient snapshot
            name = row_data.get("recipient_name") or row_data.get("name") or ""
            email = row_data.get("recipient_email") or row_data.get("email") or ""

            docs.append({
                "job_id": jid,
                "organization_id": oid,
                "import_row_id": ObjectId(r["id"]),
                "row_number": r["row_number"],
                "status": "pending",
                "certificate_id": None,
                "attempts": 0,
                "error": None,
                "recipient": {"name": name, "email": email},
                "data": row_data,
                "started_at": None,
                "completed_at": None,
                "created_at": now,
            })

        if not docs:
            return 0

        res = await cls._collection().insert_many(docs, ordered=False)
        return len(res.inserted_ids)

    @classmethod
    async def claim_next(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Atomic claim of the next pending item for a worker.
        Only one worker can claim an item.
        """
        try:
            jid = ObjectId(job_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"job_id": jid, "status": "pending"},
            {
                "$set": {
                    "status": "processing",
                    "started_at": now,
                },
                "$inc": {"attempts": 1},
            },
            return_document=True,
        )
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def claim_batch(cls, job_id: str, batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Atomically claim up to `batch_size` pending items for worker processing — P12.14.
        """
        try:
            jid = ObjectId(job_id)
        except Exception:
            return []

        now = datetime.now(timezone.utc)
        claimed = []
        cursor = cls._collection().find(
            {"job_id": jid, "status": "pending"},
            projection={"_id": 1}
        ).limit(batch_size)
        candidate_ids = [doc["_id"] async for doc in cursor]
        if not candidate_ids:
            return []

        res = await cls._collection().update_many(
            {"_id": {"$in": candidate_ids}, "status": "pending"},
            {
                "$set": {"status": "processing", "started_at": now},
                "$inc": {"attempts": 1}
            }
        )
        if res.modified_count == 0:
            return []

        cursor_claimed = cls._collection().find({"_id": {"$in": candidate_ids}, "status": "processing"})
        async for doc in cursor_claimed:
            claimed.append(cls._serialize(doc))
        return claimed

    @classmethod
    async def mark_completed(
        cls,
        item_id: str,
        certificate_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(item_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": iid},
            {
                "$set": {
                    "status": "completed",
                    "certificate_id": certificate_id,
                    "completed_at": now,
                    "error": None,
                }
            },
            return_document=True,
        )
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def mark_failed(
        cls,
        item_id: str,
        error_info: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(item_id)
        except Exception:
            return None

        now = datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": iid},
            {
                "$set": {
                    "status": "failed",
                    "error": error_info,
                    "completed_at": now,
                }
            },
            return_document=True,
        )
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def list_items(
        cls,
        job_id: str,
        status: Optional[str] = None,
        recipient_search: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return [], 0

        query: Dict[str, Any] = {"job_id": jid}
        if status:
            query["status"] = status
        if recipient_search:
            regex = {"$regex": recipient_search, "$options": "i"}
            query["$or"] = [
                {"recipient.name": regex},
                {"recipient.email": regex},
            ]

        total = await cls._collection().count_documents(query)
        skip = max(0, (page - 1) * limit)
        cursor = cls._collection().find(query).sort("row_number", 1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)

        return [cls._serialize(doc) for doc in items], total

    @classmethod
    async def get_failed_items(cls, job_id: str) -> List[Dict[str, Any]]:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return []

        cursor = cls._collection().find({
            "job_id": jid,
            "status": "failed",
        }).sort("row_number", 1)
        items = await cursor.to_list(length=10000)
        return [cls._serialize(doc) for doc in items]

    @classmethod
    async def get_by_id(cls, item_id: str, job_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(item_id)
        except Exception:
            return None

        query: Dict[str, Any] = {"_id": iid}
        if job_id:
            try:
                query["job_id"] = ObjectId(job_id)
            except Exception:
                return None

        doc = await cls._collection().find_one(query)
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def reset_failed_to_pending(cls, job_id: str) -> int:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return 0

        res = await cls._collection().update_many(
            {"job_id": jid, "status": "failed"},
            {
                "$set": {
                    "status": "pending",
                    "error": None,
                    "started_at": None,
                    "completed_at": None,
                }
            }
        )
        return res.modified_count

    @classmethod
    async def reset_single_item_to_pending(cls, item_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        try:
            iid = ObjectId(item_id)
            jid = ObjectId(job_id)
        except Exception:
            return None

        doc = await cls._collection().find_one_and_update(
            {"_id": iid, "job_id": jid, "status": "failed"},
            {
                "$set": {
                    "status": "pending",
                    "error": None,
                    "started_at": None,
                    "completed_at": None,
                }
            },
            return_document=True,
        )
        if not doc:
            return None
        return cls._serialize(doc)

    @classmethod
    async def cancel_pending_items(cls, job_id: str) -> int:
        try:
            jid = ObjectId(job_id)
        except Exception:
            return 0

        now = datetime.now(timezone.utc)
        res = await cls._collection().update_many(
            {"job_id": jid, "status": "pending"},
            {
                "$set": {
                    "status": "cancelled",
                    "completed_at": now,
                }
            }
        )
        return res.modified_count

    @classmethod
    async def reset_stale_processing_items(
        cls,
        job_id: str,
        timeout_seconds: int = 120,
        max_attempts: int = 3,
    ) -> int:
        """
        Crash recovery: find items stuck in 'processing' longer than timeout.
        If attempts < max_attempts, reset to 'pending'.
        If attempts >= max_attempts, mark as 'failed' with TIMEOUT error.
        """
        try:
            jid = ObjectId(job_id)
        except Exception:
            return 0

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)

        # 1. Stale with remaining attempts -> reset to pending
        res_reset = await cls._collection().update_many(
            {
                "job_id": jid,
                "status": "processing",
                "started_at": {"$lt": cutoff},
                "attempts": {"$lt": max_attempts},
            },
            {
                "$set": {
                    "status": "pending",
                    "started_at": None,
                }
            }
        )

        # 2. Stale with max attempts reached -> mark failed
        now = datetime.now(timezone.utc)
        await cls._collection().update_many(
            {
                "job_id": jid,
                "status": "processing",
                "started_at": {"$lt": cutoff},
                "attempts": {"$gte": max_attempts},
            },
            {
                "$set": {
                    "status": "failed",
                    "completed_at": now,
                    "error": {
                        "code": "WORKER_TIMEOUT",
                        "message": f"Processing timed out after {timeout_seconds}s and reached maximum retry attempts ({max_attempts})",
                    }
                }
            }
        )

        return res_reset.modified_count
