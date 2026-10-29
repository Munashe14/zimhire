from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_admin, require_staff
from app.schemas.equipment import (
    EquipmentCategoryCreate,
    EquipmentCategoryUpdate,
    EquipmentCategoryResponse,
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
)
from app.services.equipment_service import EquipmentService
from app.models.equipment import EquipmentStatus
from app.models.user import User

router = APIRouter(prefix="/api/equipment", tags=["Equipment"])


# Category endpoints
@router.post("/categories", response_model=EquipmentCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: EquipmentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new equipment category (admin only)."""
    service = EquipmentService(db)
    return service.create_category(category_data)


@router.get("/categories", response_model=list[EquipmentCategoryResponse])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """List all equipment categories (staff only)."""
    service = EquipmentService(db)
    categories, _ = service.list_categories(skip=skip, limit=limit)
    return categories


@router.get("/categories/{category_id}", response_model=EquipmentCategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Get a category by ID (staff only)."""
    service = EquipmentService(db)
    return service.get_category(category_id)


@router.put("/categories/{category_id}", response_model=EquipmentCategoryResponse)
def update_category(
    category_id: int,
    category_data: EquipmentCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a category (admin only)."""
    service = EquipmentService(db)
    return service.update_category(category_id, category_data)


# Equipment endpoints
@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    equipment_data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create new equipment (admin only)."""
    service = EquipmentService(db)
    return service.create_equipment(equipment_data)


@router.get("", response_model=EquipmentListResponse)
def list_equipment(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    status: Optional[EquipmentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """List equipment with optional filters (staff only)."""
    service = EquipmentService(db)
    equipment, total = service.list_equipment(
        skip=skip,
        limit=limit,
        category_id=category_id,
        status=status
    )
    return EquipmentListResponse(
        items=equipment,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Get equipment by ID (staff only)."""
    service = EquipmentService(db)
    return service.get_equipment(equipment_id)


@router.put("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update equipment (admin only)."""
    service = EquipmentService(db)
    return service.update_equipment(equipment_id, equipment_data)


@router.get("/{equipment_id}/availability")
def check_availability(
    equipment_id: int,
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Check if equipment is available for a date range (staff only)."""
    from datetime import datetime
    
    service = EquipmentService(db)
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    
    available = service.check_availability(equipment_id, start_dt, end_dt)
    return {"available": available}
