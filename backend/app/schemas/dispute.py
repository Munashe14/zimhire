from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.dispute import DisputeStatus


class DamageDisputeBase(BaseModel):
    booking_id: int
    equipment_id: int
    damage_description: str = Field(..., min_length=1)


class DamageDisputeCreate(DamageDisputeBase):
    pass


class DamageDisputeUpdate(BaseModel):
    status: Optional[DisputeStatus] = None
    resolution_notes: Optional[str] = None


class DamageDisputeResponse(DamageDisputeBase):
    id: int
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None
    status: DisputeStatus
    resolution_notes: Optional[str] = None
    decision_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DamageDisputeListResponse(BaseModel):
    items: list[DamageDisputeResponse]
    total: int
    skip: int
    limit: int
