from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from datetime import datetime
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.invoice import Invoice
from app.schemas.payment import PaymentCreate, PaymentUpdate


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Create a new payment."""
        # Check for duplicate provider transaction ID
        if payment_data.provider_transaction_id:
            existing = self.db.query(Payment).filter(
                Payment.provider_transaction_id == payment_data.provider_transaction_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Payment with this transaction ID already exists",
                )
        
        # Check for duplicate payment reference with same method
        existing = self.db.query(Payment).filter(
            Payment.payment_reference == payment_data.payment_reference,
            Payment.payment_method == payment_data.payment_method
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment with this reference and method already exists",
            )
        
        # Verify invoice if provided
        if payment_data.invoice_id:
            invoice = self.db.query(Invoice).filter(Invoice.id == payment_data.invoice_id).first()
            if not invoice:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found",
                )
        
        payment = Payment(
            invoice_id=payment_data.invoice_id,
            payment_reference=payment_data.payment_reference,
            provider_transaction_id=payment_data.provider_transaction_id,
            payment_method=payment_data.payment_method,
            amount_cents=payment_data.amount_cents,
            currency=payment_data.currency,
            status=PaymentStatus.UNMATCHED if not payment_data.invoice_id else PaymentStatus.PENDING,
            notes=payment_data.notes,
            is_simulated=1 if payment_data.is_simulated else 0,
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payment(self, payment_id: int) -> Payment:
        """Get a payment by ID."""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        return payment

    def list_payments(
        self,
        skip: int = 0,
        limit: int = 100,
        invoice_id: int = None,
        status: PaymentStatus = None,
        is_simulated: bool = None
    ) -> Tuple[list[Payment], int]:
        """List payments with optional filters."""
        query = self.db.query(Payment)
        
        if invoice_id:
            query = query.filter(Payment.invoice_id == invoice_id)
        if status:
            query = query.filter(Payment.status == status)
        if is_simulated is not None:
            query = query.filter(Payment.is_simulated == (1 if is_simulated else 0))
        
        query = query.order_by(Payment.payment_date.desc())
        
        total = query.count()
        payments = query.offset(skip).limit(limit).all()
        return payments, total

    def match_payment_to_invoice(self, payment_id: int, invoice_id: int) -> Payment:
        """Match a payment to an invoice."""
        payment = self.get_payment(payment_id)
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found",
            )
        
        # Update payment
        payment.invoice_id = invoice_id
        payment.status = PaymentStatus.MATCHED
        payment.matched_date = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(payment)
        
        # Update invoice status
        from app.services.invoice_service import InvoiceService
        invoice_service = InvoiceService(self.db)
        invoice_service.update_invoice_status(invoice)
        
        return payment

    def update_payment(self, payment_id: int, payment_data: PaymentUpdate) -> Payment:
        """Update a payment."""
        payment = self.get_payment(payment_id)
        
        update_data = payment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_unmatched_payments(self) -> list[Payment]:
        """Get all unmatched payments."""
        return self.db.query(Payment).filter(
            Payment.status == PaymentStatus.UNMATCHED
        ).order_by(Payment.payment_date.desc()).all()
