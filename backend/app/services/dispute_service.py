from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from datetime import datetime
from app.models.dispute import DamageDispute, DisputeStatus
from app.models.booking import Booking
from app.models.equipment import Equipment
from app.schemas.dispute import DamageDisputeCreate, DamageDisputeUpdate


class DisputeService:
    def __init__(self, db: Session):
        self.db = db

    def create_dispute(self, dispute_data: DamageDisputeCreate) -> DamageDispute:
        """Create a new damage dispute."""
        # Verify booking exists
        booking = self.db.query(Booking).filter(Booking.id == dispute_data.booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        
        # Verify equipment exists
        equipment = self.db.query(Equipment).filter(Equipment.id == dispute_data.equipment_id).first()
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )
        
        # Verify equipment is in the booking
        from app.models.booking import BookingItem
        booking_item = self.db.query(BookingItem).filter(
            BookingItem.booking_id == dispute_data.booking_id,
            BookingItem.equipment_id == dispute_data.equipment_id
        ).first()
        if not booking_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment not found in this booking",
            )
        
        # Check for existing open dispute
        existing = self.db.query(DamageDispute).filter(
            DamageDispute.booking_id == dispute_data.booking_id,
            DamageDispute.equipment_id == dispute_data.equipment_id,
            DamageDispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW])
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An open dispute already exists for this booking and equipment",
            )
        
        dispute = DamageDispute(
            booking_id=dispute_data.booking_id,
            equipment_id=dispute_data.equipment_id,
            status=DisputeStatus.OPEN,
            damage_description=dispute_data.damage_description,
        )
        self.db.add(dispute)
        self.db.commit()
        self.db.refresh(dispute)
        return dispute

    def get_dispute(self, dispute_id: int) -> DamageDispute:
        """Get a dispute by ID."""
        dispute = self.db.query(DamageDispute).filter(DamageDispute.id == dispute_id).first()
        if not dispute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found",
            )
        return dispute

    def list_disputes(
        self,
        skip: int = 0,
        limit: int = 100,
        status: DisputeStatus = None
    ) -> Tuple[list[DamageDispute], int]:
        """List disputes with optional filters."""
        query = self.db.query(DamageDispute)
        
        if status:
            query = query.filter(DamageDispute.status == status)
        
        query = query.order_by(DamageDispute.created_at.desc())
        
        total = query.count()
        disputes = query.offset(skip).limit(limit).all()
        return disputes, total

    def update_dispute(
        self,
        dispute_id: int,
        dispute_data: DamageDisputeUpdate,
        reviewer_id: int
    ) -> DamageDispute:
        """Update a dispute (typically by operations manager)."""
        dispute = self.get_dispute(dispute_id)
        
        update_data = dispute_data.model_dump(exclude_unset=True)
        
        # Set reviewer if status is being changed
        if "status" in update_data:
            dispute.reviewer_id = reviewer_id
            
            # Set decision date if resolving
            if update_data["status"] in [DisputeStatus.RESOLVED, DisputeStatus.CLOSED]:
                dispute.decision_date = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(dispute, field, value)
        
        self.db.commit()
        self.db.refresh(dispute)
        return dispute
