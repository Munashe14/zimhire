from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from datetime import datetime
import random
import string
from app.models.invoice import Invoice, InvoiceStatus
from app.models.client import Client
from app.models.booking import Booking
from app.models.payment import Payment, PaymentStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        while True:
            invoice_num = f"INV-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"
            existing = self.db.query(Invoice).filter(Invoice.invoice_number == invoice_num).first()
            if not existing:
                return invoice_num

    def create_invoice(self, invoice_data: InvoiceCreate) -> Invoice:
        """Create a new invoice."""
        # Verify client exists
        client = self.db.query(Client).filter(Client.id == invoice_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        
        # Verify booking if provided
        if invoice_data.booking_id:
            booking = self.db.query(Booking).filter(Booking.id == invoice_data.booking_id).first()
            if not booking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Booking not found",
                )
        
        invoice = Invoice(
            invoice_number=self._generate_invoice_number(),
            booking_id=invoice_data.booking_id,
            client_id=invoice_data.client_id,
            due_date=invoice_data.due_date,
            status=InvoiceStatus.DRAFT,
            subtotal_cents=invoice_data.subtotal_cents,
            tax_cents=invoice_data.tax_cents,
            total_cents=invoice_data.total_cents,
            currency=invoice_data.currency,
            notes=invoice_data.notes,
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_invoice(self, invoice_id: int) -> Invoice:
        """Get an invoice by ID."""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        return invoice

    def list_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: int = None,
        status: InvoiceStatus = None
    ) -> Tuple[list[Invoice], int]:
        """List invoices with optional filters."""
        query = self.db.query(Invoice)
        
        if client_id:
            query = query.filter(Invoice.client_id == client_id)
        if status:
            query = query.filter(Invoice.status == status)
        
        query = query.order_by(Invoice.issue_date.desc())
        
        total = query.count()
        invoices = query.offset(skip).limit(limit).all()
        return invoices, total

    def update_invoice(self, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
        """Update an invoice."""
        invoice = self.get_invoice(invoice_id)
        
        update_data = invoice_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        # If status is being set to ISSUED, update issue date
        if invoice_data.status == InvoiceStatus.ISSUED and invoice.status != InvoiceStatus.ISSUED:
            invoice.issue_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def calculate_paid_amount(self, invoice_id: int) -> int:
        """Calculate the total amount paid for an invoice."""
        payments = self.db.query(Payment).filter(
            Payment.invoice_id == invoice_id,
            Payment.status == PaymentStatus.MATCHED
        ).all()
        return sum(p.amount_cents for p in payments)

    def update_invoice_status(self, invoice: Invoice) -> Invoice:
        """Update invoice status based on payments."""
        paid_amount = self.calculate_paid_amount(invoice.id)
        
        if paid_amount >= invoice.total_cents:
            invoice.status = InvoiceStatus.PAID
        elif paid_amount > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        elif invoice.due_date and datetime.utcnow() > invoice.due_date:
            invoice.status = InvoiceStatus.OVERDUE
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
