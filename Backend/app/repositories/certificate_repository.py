from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo import ReturnDocument
from app.core.database import DatabaseManager
from app.repositories.user_repository import serialize_doc


def _serialize_cert(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    s = serialize_doc(doc)
    for field in ("organization_id", "template_id", "template_version_id",
                  "import_id", "import_row_id", "created_by"):
        if s.get(field):
            s[field] = str(s[field])
    return s


class SequenceRepository:
    """Atomic counter for certificate number generation — P3.50."""

    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("sequences")

    @classmethod
    async def next_val(cls, organization_id: str, key: str, year: int) -> int:
        """
        Atomically increment and return the next counter value for
        (organization_id, key, year).  Thread-safe via MongoDB $inc + upsert.
        """
        oid = ObjectId(organization_id)
        result = await cls._collection().find_one_and_update(
            {"organization_id": oid, "key": key, "year": year},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return int(result["value"])


class CertificateRepository:

    @staticmethod
    def _collection():
        return DatabaseManager.get_collection("certificates")

    @classmethod
    async def create(
        cls,
        organization_id: str,
        template_id: str,
        template_version_id: str,
        certificate_number: str,
        verification_code: str,
        recipient: Dict[str, Any],
        data: Dict[str, Any],
        template_snapshot: Dict[str, Any],
        created_by: str,
        import_id: Optional[str] = None,
        import_row_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        doc: Dict[str, Any] = {
            "organization_id": ObjectId(organization_id),
            "template_id": ObjectId(template_id),
            "template_version_id": ObjectId(template_version_id),
            "certificate_number": certificate_number,
            "verification_code": verification_code,
            "recipient": recipient,
            "data": data,
            "template_snapshot": template_snapshot,
            "status": "generating",
            "file": {
                "pdf_key": None,
                "preview_key": None,
                "pdf_size": None,
                "preview_size": None,
                "sha256": None,
            },
            "render_diagnostics": {},
            "error": None,
            "import_id": ObjectId(import_id) if import_id else None,
            "import_row_id": ObjectId(import_row_id) if import_row_id else None,
            "idempotency_key": idempotency_key,
            "created_by": ObjectId(created_by),
            "issued_at": now,
            "created_at": now,
            "updated_at": now,
        }
        res = await cls._collection().insert_one(doc)
        doc["_id"] = res.inserted_id
        return _serialize_cert(doc)

    @classmethod
    async def update_status(
        cls,
        cert_id: str,
        status: str,
        file_info: Optional[Dict[str, Any]] = None,
        render_diagnostics: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        updates: Dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }
        if file_info:
            updates["file"] = file_info
        if render_diagnostics is not None:
            updates["render_diagnostics"] = render_diagnostics
        if error is not None:
            updates["error"] = error

        doc = await cls._collection().find_one_and_update(
            {"_id": ObjectId(cert_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER
        )
        return _serialize_cert(doc)

    @classmethod
    async def get_by_id(
        cls,
        cert_id: str,
        organization_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            cid = ObjectId(cert_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": cid, "organization_id": oid})
        return _serialize_cert(doc)

    @classmethod
    async def get_by_idempotency_key(
        cls,
        key: str,
        organization_id: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return None
        doc = await cls._collection().find_one(
            {"idempotency_key": key, "organization_id": oid}
        )
        return _serialize_cert(doc)

    @classmethod
    async def get_by_verification_code(
        cls,
        verification_code: str,
    ) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"verification_code": verification_code})
        return _serialize_cert(doc)

    @classmethod
    async def list_certificates(
        cls,
        organization_id: str,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        recipient_email: Optional[str] = None,
        search: Optional[str] = None,
        program: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        verification_code: Optional[str] = None,
    ) -> tuple:
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
        if recipient_email:
            query["recipient.email"] = {"$regex": recipient_email, "$options": "i"}
        if verification_code:
            query["verification_code"] = {"$regex": verification_code, "$options": "i"}
        if program:
            query["$or"] = [
                {"data.program_name": {"$regex": program, "$options": "i"}},
                {"data.course_name": {"$regex": program, "$options": "i"}},
                {"template_snapshot.template_name": {"$regex": program, "$options": "i"}},
            ]
        if from_date and to_date:
            query["created_at"] = {"$gte": from_date, "$lte": to_date}
        elif from_date:
            query["created_at"] = {"$gte": from_date}
        elif to_date:
            query["created_at"] = {"$lte": to_date}

        if search:
            clean_search = search.strip()
            s_or = [
                {"certificate_number": {"$regex": clean_search, "$options": "i"}},
                {"recipient.name": {"$regex": clean_search, "$options": "i"}},
                {"recipient.email": {"$regex": clean_search, "$options": "i"}},
                {"verification_code": {"$regex": clean_search, "$options": "i"}},
            ]
            if "$or" in query:
                query["$and"] = [
                    {"$or": query.pop("$or")},
                    {"$or": s_or},
                ]
            else:
                query["$or"] = s_or

        total = await cls._collection().count_documents(query)
        skip = (page - 1) * limit
        cursor = (
            cls._collection()
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [_serialize_cert(d) for d in docs], total

    @classmethod
    async def get_by_sha256(cls, sha256_hash: str) -> Optional[Dict[str, Any]]:
        doc = await cls._collection().find_one({"file.sha256": sha256_hash})
        return _serialize_cert(doc)

    @classmethod
    async def revoke(
        cls,
        cert_id: str,
        organization_id: str,
        reason: Optional[str] = None,
        revoked_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            cid = ObjectId(cert_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {
            "status": "revoked",
            "revocation_reason": reason,
            "revoked_at": now,
            "revocation": {
                "revoked_at": now,
                "revoked_by": ObjectId(revoked_by) if revoked_by else None,
                "reason": reason,
                "notes": notes,
            },
            "updated_at": now,
        }
        doc = await cls._collection().find_one_and_update(
            {"_id": cid, "organization_id": oid},
            {"$set": updates},
            return_document=ReturnDocument.AFTER
        )
        return _serialize_cert(doc)

    @classmethod
    async def restore(
        cls,
        cert_id: str,
        organization_id: str,
        restored_by: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            cid = ObjectId(cert_id)
            oid = ObjectId(organization_id)
        except Exception:
            return None
        now = datetime.now(timezone.utc)
        updates: Dict[str, Any] = {
            "status": "generated",
            "revoked_at": None,
            "revocation_reason": None,
            "revocation": None,
            "restored_at": now,
            "restored_by": ObjectId(restored_by) if restored_by else None,
            "updated_at": now,
        }
        doc = await cls._collection().find_one_and_update(
            {"_id": cid, "organization_id": oid, "status": "revoked"},
            {"$set": updates},
            return_document=ReturnDocument.AFTER
        )
        return _serialize_cert(doc)

    @classmethod
    async def bulk_revoke(
        cls,
        cert_ids: List[str],
        organization_id: str,
        reason: str,
        revoked_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> tuple:
        try:
            oid = ObjectId(organization_id)
        except Exception:
            return 0, cert_ids

        valid_cids = []
        failed_ids = []
        for cid_str in cert_ids:
            try:
                valid_cids.append(ObjectId(cid_str))
            except Exception:
                failed_ids.append(cid_str)

        if not valid_cids:
            return 0, failed_ids

        now = datetime.now(timezone.utc)
        res = await cls._collection().update_many(
            {"_id": {"$in": valid_cids}, "organization_id": oid, "status": {"$ne": "revoked"}},
            {
                "$set": {
                    "status": "revoked",
                    "revocation_reason": reason,
                    "revoked_at": now,
                    "revocation": {
                        "revoked_at": now,
                        "revoked_by": ObjectId(revoked_by) if revoked_by else None,
                        "reason": reason,
                        "notes": notes,
                    },
                    "updated_at": now,
                }
            }
        )
        return res.modified_count, failed_ids

    @classmethod
    async def update_email_delivery_status(
        cls,
        certificate_id: str,
        status: str,
        delivery_id: str,
        sent_at: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            cid = ObjectId(certificate_id)
        except Exception:
            return None
        now = sent_at or datetime.now(timezone.utc)
        doc = await cls._collection().find_one_and_update(
            {"_id": cid},
            {
                "$set": {
                    "email_delivery": {
                        "status": status,
                        "delivery_id": str(delivery_id),
                        "last_sent_at": now,
                    },
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return _serialize_cert(doc)

