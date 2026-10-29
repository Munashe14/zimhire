from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ClientType(str, enum.Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    client_type = Column(SQLEnum(ClientType), default=ClientType.INDIVIDUAL)
    account_status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
