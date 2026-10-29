from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from typing import Tuple, List
from datetime import datetime, timedelta
import random
import string
from app.models.booking import Booking, BookingItem, BookingStatus
from app.models.equipment import Equipment, EquipmentStatus
from app.models.client import Client
from app.schemas.booking import BookingCreate, BookingUpdate, AvailabilityCheckRequest


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_booking_reference(self) -> str:
        """Generate a unique booking reference."""
        while True:
            ref = f"ZMH-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
            existing = self.db.query(Booking).filter(Booking.booking_reference == ref).first()
            if not existing:
                return ref

    def check_availability(
        self,
        equipment_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> List[dict]:
        """Check availability for multiple equipment items."""
        from app.schemas.booking import AvailabilityCheckResponse
        
        results = []
        for equipment_id in equipment_ids:
            equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
            if not equipment:
                results.append({
                    "equipment_id": equipment_id,
                    "available": False,
                    "reason": "Equipment not found"
                })
                continue
            
            # Check equipment status
            if equipment.status != EquipmentStatus.AVAILABLE:
                results.append({
                    "equipment_id": equipment_id,
                    "available": False,
                    "reason": f"Equipment status is {equipment.status.value}"
                })
                continue
            
            # Check for overlapping bookings
            overlapping = self.db.query(Booking).join(BookingItem).filter(
                BookingItem.equipment_id == equipment_id,
                Booking.status.in_([
                    BookingStatus.CONFIRMED,
                    BookingStatus.ACTIVE
                ]),
                Booking.end_date > start_date,
                Booking.start_date < end_date
            ).first()
            
            if overlapping:
                results.append({
                    "equipment_id": equipment_id,
                    "available": False,
                    "reason": "Equipment already booked for this period"
                })
            else:
                results.append({
                    "equipment_id": equipment_id,
                    "available": True,
                    "reason": None
                })
        
        return results

    def create_booking(self, booking_data: BookingCreate, user_id: int) -> Booking:
        """Create a new booking with conflict prevention."""
        # Validate date range
        if booking_data.end_date <= booking_data.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date",
            )
        
        # Verify client exists
        client = self.db.query(Client).filter(Client.id == booking_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client not found",
            )
        
        # Check availability for all equipment
        equipment_ids = [item.equipment_id for item in booking_data.equipment_items]
        availability = self.check_availability(equipment_ids, booking_data.start_date, booking_data.end_date)
        
        unavailable = [a for a in availability if not a["available"]]
        if unavailable:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Equipment not available: {', '.join([a['reason'] for a in unavailable])}",
            )
        
        # Calculate total amount
        # Rental period: end_date is exclusive, so we calculate days between start and end
        rental_days = (booking_data.end_date - booking_data.start_date).days
        if rental_days < 1:
            rental_days = 1  # Minimum 1 day
        
        total_cents = 0
        for item in booking_data.equipment_items:
            total_cents += item.daily_rate * rental_days
        
        # Use SERIALIZABLE isolation to prevent concurrent booking conflicts
        self.db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
        
        try:
            # Double-check availability within transaction
            availability = self.check_availability(equipment_ids, booking_data.start_date, booking_data.end_date)
            unavailable = [a for a in availability if not a["available"]]
            if unavailable:
                self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Concurrent booking conflict - equipment no longer available",
                )
            
            # Create booking
            booking = Booking(
                booking_reference=self._generate_booking_reference(),
                client_id=booking_data.client_id,
                created_by_user_id=user_id,
                start_date=booking_data.start_date,
                end_date=booking_data.end_date,
                status=BookingStatus.PENDING,
                total_amount=total_cents,
                currency="USD",
                notes=booking_data.notes,
            )
            self.db.add(booking)
            self.db.flush()  # Get booking ID
            
            # Create booking items
            for item_data in booking_data.equipment_items:
                booking_item = BookingItem(
                    booking_id=booking.id,
                    equipment_id=item_data.equipment_id,
                    daily_rate=item_data.daily_rate,
                    currency=item_data.currency,
                )
                self.db.add(booking_item)
            
            self.db.commit()
            self.db.refresh(booking)
            return booking
        
        except Exception as e:
            self.db.rollback()
            raise e

    def get_booking(self, booking_id: int) -> Booking:
        """Get a booking by ID."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        return booking

    def list_bookings(
        self,
        skip: int = 0,
        limit: int = 100,
        client_id: int = None,
        status: BookingStatus = None
    ) -> Tuple[List[Booking], int]:
        """List bookings with optional filters."""
        query = self.db.query(Booking)
        
        if client_id:
            query = query.filter(Booking.client_id == client_id)
        if status:
            query = query.filter(Booking.status == status)
        
        query = query.order_by(Booking.created_at.desc())
        
        total = query.count()
        bookings = query.offset(skip).limit(limit).all()
        return bookings, total

    def update_booking(self, booking_id: int, booking_data: BookingUpdate) -> Booking:
        """Update a booking (typically status changes)."""
        booking = self.get_booking(booking_id)
        
        update_data = booking_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        # Handle status transitions
        if booking_data.status == BookingStatus.CONFIRMED:
            # Mark equipment as reserved
            for item in booking.booking_items:
                equipment = self.db.query(Equipment).filter(Equipment.id == item.equipment_id).first()
                if equipment:
                    equipment.status = EquipmentStatus.RESERVED
        
        elif booking_data.status == BookingStatus.ACTIVE:
            # Mark equipment as rented out
            for item in booking.booking_items:
                equipment = self.db.query(Equipment).filter(Equipment.id == item.equipment_id).first()
                if equipment:
                    equipment.status = EquipmentStatus.RENTED_OUT
        
        elif booking_data.status == BookingStatus.COMPLETED:
            # Mark equipment as available
            for item in booking.booking_items:
                equipment = self.db.query(Equipment).filter(Equipment.id == item.equipment_id).first()
                if equipment:
                    equipment.status = EquipmentStatus.AVAILABLE
        
        elif booking_data.status == BookingStatus.CANCELLED:
            # Release equipment back to available
            for item in booking.booking_items:
                equipment = self.db.query(Equipment).filter(Equipment.id == item.equipment_id).first()
                if equipment and equipment.status in [EquipmentStatus.RESERVED, EquipmentStatus.RENTED_OUT]:
                    equipment.status = EquipmentStatus.AVAILABLE
        
        self.db.commit()
        self.db.refresh(booking)
        return booking
