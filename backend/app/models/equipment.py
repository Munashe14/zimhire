from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    RENTED_OUT = "rented_out"
    UNDER_MAINTENANCE = "under_maintenance"
    UNAVAILABLE = "unavailable"


class EquipmentCategory(Base):
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    equipment = relationship("Equipment", back_populates="category")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    identification_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("equipment_categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    daily_rate = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(EquipmentStatus), default=EquipmentStatus.AVAILABLE, nullable=False)
    maintenance_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint('daily_rate >= 0', name='check_daily_rate_positive'),
    )

    # Relationships
    category = relationship("EquipmentCategory", back_populates="equipment")
    booking_items = relationship("BookingItem", back_populates="equipment")
    condition_records = relationship("ConditionRecord", back_populates="equipment")
    damage_disputes = relationship("DamageDispute", back_populates="equipment")
