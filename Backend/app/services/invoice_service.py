from __future__ import annotations
from typing import Dict, Any, Optional
from datetime import datetime
from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.invoice import InvoiceResponse, InvoiceListResponse
from app.core.exceptions import NotFoundError


class InvoiceService:
    @classmethod
    async def list_invoices(
        cls,
        org_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> InvoiceListResponse:
        """List customer invoices for an organization."""
        invoices = await InvoiceRepository.list_by_org(org_id=org_id, skip=skip, limit=limit)
        return InvoiceListResponse(
            items=[InvoiceResponse(**inv) for inv in invoices],
            total=len(invoices)
        )

    @classmethod
    async def get_invoice(cls, invoice_id: str, org_id: str) -> InvoiceResponse:
        """Fetch single invoice by ID with strict tenant isolation."""
        inv = await InvoiceRepository.get_by_id(invoice_id=invoice_id, org_id=org_id)
        if not inv:
            raise NotFoundError(message="Invoice not found", code="INVOICE_NOT_FOUND")
        return InvoiceResponse(**inv)

    @classmethod
    async def record_paid_invoice(
        cls,
        organization_id: str,
        amount: int,
        invoice_number: str,
        currency: str = "INR",
        subscription_id: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        provider_invoice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record paid invoice upon successful webhook confirmation."""
        return await InvoiceRepository.create(
            organization_id=organization_id,
            amount=amount,
            invoice_number=invoice_number,
            currency=currency,
            subscription_id=subscription_id,
            status="paid",
            period_start=period_start,
            period_end=period_end,
            provider_invoice_id=provider_invoice_id
        )
