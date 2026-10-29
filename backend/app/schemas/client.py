from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from app.models.client import ClientType, AccountStatus


class ClientBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    business_name: Optional[str] = Field(None, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    client_type: ClientType = ClientType.INDIVIDUAL
    account_status: AccountStatus = AccountStatus.ACTIVE


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    business_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    client_type: Optional[ClientType] = None
    account_status: Optional[AccountStatus] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    skip: int
    limit: int
