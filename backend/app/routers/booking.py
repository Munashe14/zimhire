from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_booking_clerk, require_admin
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    BookingListResponse,
    AvailabilityCheckRequest,
    AvailabilityCheckResponse,
)
from app.services.booking_service import BookingService
from app.models.booking import BookingStatus
from app.models.user import User

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/check-availability", response_model=list[AvailabilityCheckResponse])
def check_availability(
    check_request: AvailabilityCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Check availability for multiple equipment items (booking clerk or admin)."""
    service = BookingService(db)
    results = service.check_availability(
        check_request.equipment_ids,
        check_request.start_date,
        check_request.end_date
    )
    return [AvailabilityCheckResponse(**r) for r in results]


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Create a new booking (booking clerk or admin)."""
    service = BookingService(db)
    return service.create_booking(booking_data, current_user.id)


@router.get("", response_model=BookingListResponse)
def list_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    status: Optional[BookingStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """List bookings with optional filters (booking clerk or admin)."""
    service = BookingService(db)
    bookings, total = service.list_bookings(
        skip=skip,
        limit=limit,
        client_id=client_id,
        status=status
    )
    return BookingListResponse(
        items=bookings,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Get a booking by ID (booking clerk or admin)."""
    service = BookingService(db)
    return service.get_booking(booking_id)


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_booking_clerk)
):
    """Update a booking (booking clerk or admin)."""
    service = BookingService(db)
    return service.update_booking(booking_id, booking_data)
