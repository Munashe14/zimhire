from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.invoice import InvoiceStatus


class InvoiceBase(BaseModel):
    booking_id: Optional[int] = None
    client_id: int
    due_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)


class InvoiceCreate(InvoiceBase):
    subtotal_cents: int = Field(..., ge=0)
    tax_cents: int = Field(default=0, ge=0)
    total_cents: int = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)


class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: str
    issue_date: datetime
    status: InvoiceStatus
    subtotal_cents: int
    tax_cents: int
    total_cents: int
    currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    client_name: Optional[str] = None
    paid_amount_cents: int = 0

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    skip: int
    limit: int
