from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_operations_manager, require_admin
from app.schemas.dispute import (
    DamageDisputeCreate,
    DamageDisputeUpdate,
    DamageDisputeResponse,
    DamageDisputeListResponse,
)
from app.services.dispute_service import DisputeService
from app.models.dispute import DisputeStatus
from app.models.user import User

router = APIRouter(prefix="/api/disputes", tags=["Damage Disputes"])


@router.post("", response_model=DamageDisputeResponse, status_code=status.HTTP_201_CREATED)
def create_dispute(
    dispute_data: DamageDisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Create a new damage dispute (operations manager or admin)."""
    service = DisputeService(db)
    return service.create_dispute(dispute_data)


@router.get("", response_model=DamageDisputeListResponse)
def list_disputes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[DisputeStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """List disputes with optional filters (operations manager or admin)."""
    service = DisputeService(db)
    disputes, total = service.list_disputes(
        skip=skip,
        limit=limit,
        status=status
    )
    return DamageDisputeListResponse(
        items=disputes,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{dispute_id}", response_model=DamageDisputeResponse)
def get_dispute(
    dispute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get a dispute by ID (operations manager or admin)."""
    service = DisputeService(db)
    return service.get_dispute(dispute_id)


@router.put("/{dispute_id}", response_model=DamageDisputeResponse)
def update_dispute(
    dispute_id: int,
    dispute_data: DamageDisputeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Update a dispute (operations manager or admin)."""
    service = DisputeService(db)
    return service.update_dispute(dispute_id, dispute_data, current_user.id)
