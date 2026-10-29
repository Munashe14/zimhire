from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.deps import require_depot_supervisor, require_admin
from app.schemas.inspection import (
    ConditionRecordCreate,
    ConditionRecordUpdate,
    ConditionRecordResponse,
    InspectionComparison,
)
from app.services.inspection_service import InspectionService
from app.models.inspection import InspectionType
from app.models.user import User

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])


@router.post("", response_model=ConditionRecordResponse, status_code=status.HTTP_201_CREATED)
def create_condition_record(
    booking_id: int = Form(...),
    equipment_id: int = Form(...),
    inspection_type: InspectionType = Form(...),
    condition: str = Form(...),
    notes: Optional[str] = Form(None),
    damage_flagged: bool = Form(False),
    photos: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_depot_supervisor)
):
    """Create a new condition record with optional photos (depot supervisor or admin)."""
    from app.schemas.inspection import ConditionRecordCreate
    
    record_data = ConditionRecordCreate(
        booking_id=booking_id,
        equipment_id=equipment_id,
        inspection_type=inspection_type,
        condition=condition,
        notes=notes,
        damage_flagged=damage_flagged,
    )
    
    service = InspectionService(db)
    return service.create_condition_record(record_data, current_user.id, photos)


@router.get("", response_model=list[ConditionRecordResponse])
def list_condition_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    booking_id: Optional[int] = Query(None),
    equipment_id: Optional[int] = Query(None),
    inspection_type: Optional[InspectionType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_depot_supervisor)
):
    """List condition records with optional filters (depot supervisor or admin)."""
    service = InspectionService(db)
    records, _ = service.list_condition_records(
        skip=skip,
        limit=limit,
        booking_id=booking_id,
        equipment_id=equipment_id,
        inspection_type=inspection_type
    )
    return records


@router.get("/{record_id}", response_model=ConditionRecordResponse)
def get_condition_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_depot_supervisor)
):
    """Get a condition record by ID (depot supervisor or admin)."""
    service = InspectionService(db)
    return service.get_condition_record(record_id)


@router.get("/compare/{booking_id}/{equipment_id}", response_model=InspectionComparison)
def compare_inspections(
    booking_id: int,
    equipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_depot_supervisor)
):
    """Compare dispatch and return inspections for a booking (depot supervisor or admin)."""
    service = InspectionService(db)
    comparison = service.compare_inspections(booking_id, equipment_id)
    return InspectionComparison(
        dispatch=comparison["dispatch"],
        return_inspection=comparison["return_inspection"],
        damage_detected=comparison["damage_detected"]
    )


@router.put("/{record_id}", response_model=ConditionRecordResponse)
def update_condition_record(
    record_id: int,
    record_data: ConditionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_depot_supervisor)
):
    """Update a condition record (depot supervisor or admin)."""
    service = InspectionService(db)
    return service.update_condition_record(record_id, record_data)
