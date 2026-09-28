from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.core.database import DatabaseManager


class InvoiceRepository:
    COLLECTION_NAME = "invoices"

    @classmethod
    def _collection(cls):
        return DatabaseManager.get_collection(cls.COLLECTION_NAME)

    @classmethod
    async def create(
        cls,
        organization_id: str,
        amount: int,
        invoice_number: str,
        currency: str = "INR",
        subscription_id: Optional[str] = None,
        status: str = "paid",
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        paid_at: Optional[datetime] = None,
        invoice_pdf_url: Optional[str] = None,
        hosted_invoice_url: Optional[str] = None,
        provider_invoice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new invoice record."""
        now = datetime.now(timezone.utc)
        doc = {
            "organization_id": str(organization_id),
            "subscription_id": str(subscription_id) if subscription_id else None,
            "invoice_number": invoice_number,
            "amount": amount,
            "currency": currency,
            "status": status,
            "period_start": period_start or now,
            "period_end": period_end or now,
            "paid_at": paid_at or (now if status == "paid" else None),
            "invoice_pdf_url": invoice_pdf_url,
            "hosted_invoice_url": hosted_invoice_url,
            "provider_invoice_id": provider_invoice_id,
            "created_at": now
        }
        res = await cls._collection().insert_one(doc)
        doc["id"] = str(res.inserted_id)
        return doc

    @classmethod
    async def get_by_id(cls, invoice_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """Fetch invoice by ID ensuring strict organization isolation."""
        try:
            oid = ObjectId(invoice_id)
        except Exception:
            return None
        doc = await cls._collection().find_one({"_id": oid, "organization_id": str(org_id)})
        if not doc:
            return None
        doc["id"] = str(doc.pop("_id"))
        return doc

    @classmethod
    async def list_by_org(cls, org_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """List invoices for organization sorted newest first."""
        cursor = cls._collection().find({"organization_id": str(org_id)}).sort("created_at", -1).skip(skip).limit(limit)
        items = await cursor.to_list(length=limit)
        for doc in items:
            doc["id"] = str(doc.pop("_id"))
        return items
