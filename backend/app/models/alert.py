from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AlertType(str, enum.Enum):
    OVERDUE_EQUIPMENT = "overdue_equipment"
    MAINTENANCE_DUE = "maintenance_due"
    DAMAGE_REPORTED = "damage_reported"
    PAYMENT_MISMATCH = "payment_mismatch"
    BOOKING_CONFLICT = "booking_conflict"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    message = Column(String(1000), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, nullable=False)
    acknowledged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        Index('idx_alert_type_status', 'alert_type', 'status'),
        Index('idx_alert_booking', 'booking_id'),
    )

    # Relationships
    booking = relationship("Booking")
    equipment = relationship("Equipment")
    acknowledged_by = relationship("User")
