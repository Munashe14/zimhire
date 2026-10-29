from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    ECOCASH = "ecocash"
    ZIPIT = "zipit"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    PARTIALLY_MATCHED = "partially_matched"
    FAILED = "failed"
    UNMATCHED = "unmatched"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    payment_reference = Column(String(100), nullable=False, index=True)
    provider_transaction_id = Column(String(100), unique=True, nullable=True, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    amount_cents = Column(Integer, nullable=False)  # Stored in cents
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.UNMATCHED, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    matched_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(1000), nullable=True)
    is_simulated = Column(Integer, default=0)  # Boolean as integer for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('amount_cents > 0', name='check_payment_amount_positive'),
        UniqueConstraint('payment_reference', 'payment_method', name='uq_payment_reference_method'),
        Index('idx_payment_invoice', 'invoice_id'),
    )

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
