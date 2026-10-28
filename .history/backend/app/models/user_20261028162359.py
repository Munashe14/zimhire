from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    CLERK = "clerk"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    CLIENT = "client"

    # Backward-compatible aliases for older code paths and seed data.
    ADMIN = "clerk"
    BOOKING_CLERK = "clerk"
    DEPOT_SUPERVISOR = "supervisor"
    OPERATIONS_MANAGER = "manager"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    bookings = relationship("Booking", back_populates="created_by_user")
    condition_records = relationship("ConditionRecord", back_populates="inspector")
    damage_disputes = relationship("DamageDispute", back_populates="reviewer")
    audit_logs = relationship("AuditLog", back_populates="user")
