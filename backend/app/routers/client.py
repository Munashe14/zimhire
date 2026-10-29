from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_booking_clerk, require_admin
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
)
from app.services.client_service import ClientService
from app.models.client import ClientType, AccountStatus
from app.models.user import User

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Create a new client (booking clerk or admin)."""
    service = ClientService(db)
    return service.create_client(client_data)


@router.get("", response_model=ClientListResponse)
def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_type: Optional[ClientType] = Query(None),
    account_status: Optional[AccountStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """List clients with optional filters (booking clerk or admin)."""
    service = ClientService(db)
    clients, total = service.list_clients(
        skip=skip,
        limit=limit,
        client_type=client_type,
        account_status=account_status,
        search=search
    )
    return ClientListResponse(
        items=clients,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Get a client by ID (booking clerk or admin)."""
    service = ClientService(db)
    return service.get_client(client_id)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Update a client (booking clerk or admin)."""
    service = ClientService(db)
    return service.update_client(client_id, client_data)
