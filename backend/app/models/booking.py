from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    total_amount = Column(Integer, nullable=False)  # Stored in cents to avoid floating point
    currency = Column(String(3), default="USD")
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_end_date_after_start_date'),
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
        Index('idx_booking_dates', 'start_date', 'end_date'),
    )

    # Relationships
    client = relationship("Client", back_populates="bookings")
    created_by_user = relationship("User", back_populates="bookings")
    booking_items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="booking")


class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    daily_rate = Column(Integer, nullable=False)  # Stored in cents
    currency = Column(String(3), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('daily_rate >= 0', name='check_booking_item_rate_positive'),
    )

    # Relationships
    booking = relationship("Booking", back_populates="booking_items")
    equipment = relationship("Equipment", back_populates="booking_items")
