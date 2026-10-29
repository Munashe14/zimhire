from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    subtotal_cents = Column(Integer, nullable=False)  # Stored in cents
    tax_cents = Column(Integer, default=0)  # Stored in cents
    total_cents = Column(Integer, nullable=False)  # Stored in cents
    currency = Column(String(3), default="USD")
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('subtotal_cents >= 0', name='check_subtotal_positive'),
        CheckConstraint('tax_cents >= 0', name='check_tax_positive'),
        CheckConstraint('total_cents >= 0', name='check_total_positive'),
        Index('idx_invoice_client', 'client_id'),
    )

    # Relationships
    booking = relationship("Booking", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")
