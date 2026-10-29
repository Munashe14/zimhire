from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    invoice_id: Optional[int] = None
    payment_reference: str = Field(..., min_length=1, max_length=100)
    payment_method: PaymentMethod
    amount_cents: int = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = Field(None, max_length=1000)


class PaymentCreate(PaymentBase):
    provider_transaction_id: Optional[str] = Field(None, max_length=100)
    is_simulated: bool = False


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    invoice_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)


class PaymentResponse(PaymentBase):
    id: int
    provider_transaction_id: Optional[str] = None
    status: PaymentStatus
    payment_date: datetime
    matched_date: Optional[datetime] = None
    is_simulated: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    invoice_number: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    skip: int
    limit: int


class PaymentMatchRequest(BaseModel):
    payment_id: int
    invoice_id: int


class UnmatchedPaymentSummary(BaseModel):
    total_amount_cents: int
    count: int
    payments: List[PaymentResponse]
