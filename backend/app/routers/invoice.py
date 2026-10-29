from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_booking_clerk, require_admin
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
)
from app.services.invoice_service import InvoiceService
from app.models.invoice import InvoiceStatus
from app.models.user import User

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Create a new invoice (booking clerk or admin)."""
    service = InvoiceService(db)
    return service.create_invoice(invoice_data)


@router.get("", response_model=InvoiceListResponse)
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    status: Optional[InvoiceStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """List invoices with optional filters (booking clerk or admin)."""
    service = InvoiceService(db)
    invoices, total = service.list_invoices(
        skip=skip,
        limit=limit,
        client_id=client_id,
        status=status
    )
    return InvoiceListResponse(
        items=invoices,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Get an invoice by ID (booking clerk or admin)."""
    service = InvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    # Calculate paid amount
    paid_amount = service.calculate_paid_amount(invoice_id)
    invoice.paid_amount_cents = paid_amount
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Update an invoice (booking clerk or admin)."""
    service = InvoiceService(db)
    return service.update_invoice(invoice_id, invoice_data)


@router.post("/{invoice_id}/issue", response_model=InvoiceResponse)
def issue_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Issue an invoice (change status to ISSUED)."""
    service = InvoiceService(db)
    return service.update_invoice(invoice_id, InvoiceUpdate(status=InvoiceStatus.ISSUED))
