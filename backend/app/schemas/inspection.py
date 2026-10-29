from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.inspection import InspectionType


class ConditionPhotoBase(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    mime_type: str


class ConditionPhotoResponse(ConditionPhotoBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ConditionRecordBase(BaseModel):
    booking_id: int
    equipment_id: int
    inspection_type: InspectionType
    condition: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = None
    damage_flagged: bool = False


class ConditionRecordCreate(ConditionRecordBase):
    pass


class ConditionRecordUpdate(BaseModel):
    condition: Optional[str] = Field(None, min_length=1, max_length=50)
    notes: Optional[str] = None
    damage_flagged: Optional[bool] = None


class ConditionRecordResponse(ConditionRecordBase):
    id: int
    inspector_id: int
    inspector_name: Optional[str] = None
    inspection_date: datetime
    created_at: datetime
    photos: List[ConditionPhotoResponse] = []

    class Config:
        from_attributes = True


class InspectionComparison(BaseModel):
    dispatch: Optional[ConditionRecordResponse] = None
    return_inspection: Optional[ConditionRecordResponse] = None
    damage_detected: bool
