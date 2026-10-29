from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.equipment import EquipmentStatus


class EquipmentCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class EquipmentCategoryCreate(EquipmentCategoryBase):
    pass


class EquipmentCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class EquipmentCategoryResponse(EquipmentCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipmentBase(BaseModel):
    identification_number: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    category_id: int
    description: Optional[str] = None
    specifications: Optional[str] = None
    daily_rate: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    status: EquipmentStatus = EquipmentStatus.AVAILABLE
    maintenance_notes: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    description: Optional[str] = None
    specifications: Optional[str] = None
    daily_rate: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    status: Optional[EquipmentStatus] = None
    maintenance_notes: Optional[str] = None


class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[EquipmentCategoryResponse] = None

    class Config:
        from_attributes = True


class EquipmentListResponse(BaseModel):
    items: list[EquipmentResponse]
    total: int
    skip: int
    limit: int
