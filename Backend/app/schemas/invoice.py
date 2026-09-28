from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class InvoiceResponse(BaseModel):
    id: str
    organization_id: str
    subscription_id: Optional[str] = None
    invoice_number: str
    amount: int = Field(..., description="Invoice total amount in lowest currency denomination or units")
    currency: str = "INR"
    status: str = Field(..., description="'draft', 'open', 'paid', 'failed', 'void'")
    period_start: datetime
    period_end: datetime
    paid_at: Optional[datetime] = None
    invoice_pdf_url: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    created_at: datetime


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
