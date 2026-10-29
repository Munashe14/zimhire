from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.booking import BookingStatus


class BookingItemBase(BaseModel):
    equipment_id: int
    daily_rate: int  # Stored in cents
    currency: str = "USD"


class BookingItemCreate(BookingItemBase):
    pass


class BookingItemResponse(BookingItemBase):
    id: int
    equipment_name: Optional[str] = None
    equipment_identification: Optional[str] = None

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    client_id: int
    start_date: datetime
    end_date: datetime
    notes: Optional[str] = Field(None, max_length=1000)


class BookingCreate(BookingBase):
    equipment_items: List[BookingItemCreate]


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BookingResponse(BookingBase):
    id: int
    booking_reference: str
    created_by_user_id: int
    status: BookingStatus
    total_amount: int  # Stored in cents
    currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    client_name: Optional[str] = None
    booking_items: List[BookingItemResponse] = []

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    skip: int
    limit: int


class AvailabilityCheckRequest(BaseModel):
    equipment_ids: List[int]
    start_date: datetime
    end_date: datetime


class AvailabilityCheckResponse(BaseModel):
    equipment_id: int
    available: bool
    reason: Optional[str] = None
