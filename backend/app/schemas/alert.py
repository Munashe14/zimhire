from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.alert import AlertType, AlertStatus


class AlertBase(BaseModel):
    alert_type: AlertType
    booking_id: Optional[int] = None
    equipment_id: Optional[int] = None
    message: str = Field(..., min_length=1, max_length=1000)


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None


class AlertResponse(AlertBase):
    id: int
    status: AlertStatus
    acknowledged_by_id: Optional[int] = None
    acknowledged_by_name: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    skip: int
    limit: int
