from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InspectionType(str, enum.Enum):
    DISPATCH = "dispatch"
    RETURN = "return"


class ConditionRecord(Base):
    __tablename__ = "condition_records"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    inspection_type = Column(SQLEnum(InspectionType), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_date = Column(DateTime(timezone=True), server_default=func.now())
    condition = Column(String(50), nullable=False)  # e.g., "Excellent", "Good", "Fair", "Poor"
    notes = Column(Text, nullable=True)
    damage_flagged = Column(Integer, default=0)  # Boolean as integer for compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    booking = relationship("Booking")
    equipment = relationship("Equipment", back_populates="condition_records")
    inspector = relationship("User", back_populates="condition_records")
    photos = relationship("ConditionPhoto", back_populates="condition_record", cascade="all, delete-orphan")


class ConditionPhoto(Base):
    __tablename__ = "condition_photos"

    id = Column(Integer, primary_key=True, index=True)
    condition_record_id = Column(Integer, ForeignKey("condition_records.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    condition_record = relationship("ConditionRecord", back_populates="photos")
