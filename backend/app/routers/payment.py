from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_booking_clerk, require_operations_manager, require_admin
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentMatchRequest,
    UnmatchedPaymentSummary,
)
from app.services.payment_service import PaymentService
from app.models.payment import PaymentStatus
from app.models.user import User

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Create a new payment (booking clerk or admin)."""
    service = PaymentService(db)
    return service.create_payment(payment_data)


@router.get("", response_model=PaymentListResponse)
def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    invoice_id: Optional[int] = Query(None),
    status: Optional[PaymentStatus] = Query(None),
    is_simulated: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """List payments with optional filters (booking clerk or admin)."""
    service = PaymentService(db)
    payments, total = service.list_payments(
        skip=skip,
        limit=limit,
        invoice_id=invoice_id,
        status=status,
        is_simulated=is_simulated
    )
    return PaymentListResponse(
        items=payments,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/unmatched", response_model=UnmatchedPaymentSummary)
def get_unmatched_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get all unmatched payments (operations manager or admin)."""
    service = PaymentService(db)
    payments = service.get_unmatched_payments()
    total_amount = sum(p.amount_cents for p in payments)
    return UnmatchedPaymentSummary(
        total_amount_cents=total_amount,
        count=len(payments),
        payments=payments
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Get a payment by ID (booking clerk or admin)."""
    service = PaymentService(db)
    return service.get_payment(payment_id)


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Update a payment (booking clerk or admin)."""
    service = PaymentService(db)
    return service.update_payment(payment_id, payment_data)


@router.post("/match", response_model=PaymentResponse)
def match_payment(
    match_request: PaymentMatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Match a payment to an invoice (operations manager or admin)."""
    service = PaymentService(db)
    return service.match_payment_to_invoice(match_request.payment_id, match_request.invoice_id)
