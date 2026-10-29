from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from app.models.equipment import Equipment, EquipmentCategory, EquipmentStatus
from app.models.booking import BookingItem
from app.schemas.equipment import (
    EquipmentCategoryCreate,
    EquipmentCategoryUpdate,
    EquipmentCreate,
    EquipmentUpdate,
)


class EquipmentService:
    def __init__(self, db: Session):
        self.db = db

    # Category methods
    def create_category(self, category_data: EquipmentCategoryCreate) -> EquipmentCategory:
        """Create a new equipment category."""
        existing = self.db.query(EquipmentCategory).filter(
            EquipmentCategory.name == category_data.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )
        
        category = EquipmentCategory(**category_data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> EquipmentCategory:
        """Get a category by ID."""
        category = self.db.query(EquipmentCategory).filter(
            EquipmentCategory.id == category_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        return category

    def list_categories(self, skip: int = 0, limit: int = 100) -> Tuple[list[EquipmentCategory], int]:
        """List all categories with pagination."""
        categories = self.db.query(EquipmentCategory).offset(skip).limit(limit).all()
        total = self.db.query(EquipmentCategory).count()
        return categories, total

    def update_category(self, category_id: int, category_data: EquipmentCategoryUpdate) -> EquipmentCategory:
        """Update a category."""
        category = self.get_category(category_id)
        
        if category_data.name and category_data.name != category.name:
            existing = self.db.query(EquipmentCategory).filter(
                EquipmentCategory.name == category_data.name
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists",
                )
        
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category

    # Equipment methods
    def create_equipment(self, equipment_data: EquipmentCreate) -> Equipment:
        """Create new equipment."""
        # Verify category exists
        category = self.db.query(EquipmentCategory).filter(
            EquipmentCategory.id == equipment_data.category_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )
        
        # Check for duplicate identification number
        existing = self.db.query(Equipment).filter(
            Equipment.identification_number == equipment_data.identification_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment identification number already exists",
            )
        
        equipment = Equipment(**equipment_data.model_dump())
        self.db.add(equipment)
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def get_equipment(self, equipment_id: int) -> Equipment:
        """Get equipment by ID."""
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )
        return equipment

    def list_equipment(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: int = None,
        status: EquipmentStatus = None
    ) -> Tuple[list[Equipment], int]:
        """List equipment with optional filters."""
        query = self.db.query(Equipment)
        
        if category_id:
            query = query.filter(Equipment.category_id == category_id)
        if status:
            query = query.filter(Equipment.status == status)
        
        total = query.count()
        equipment = query.offset(skip).limit(limit).all()
        return equipment, total

    def update_equipment(self, equipment_id: int, equipment_data: EquipmentUpdate) -> Equipment:
        """Update equipment."""
        equipment = self.get_equipment(equipment_id)
        
        # Check category if updating
        if equipment_data.category_id:
            category = self.db.query(EquipmentCategory).filter(
                EquipmentCategory.id == equipment_data.category_id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found",
                )
        
        update_data = equipment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(equipment, field, value)
        
        self.db.commit()
        self.db.refresh(equipment)
        return equipment

    def check_availability(
        self,
        equipment_id: int,
        start_date,
        end_date
    ) -> bool:
        """Check if equipment is available for the given date range."""
        from app.models.booking import Booking, BookingStatus
        
        equipment = self.get_equipment(equipment_id)
        
        # Check if equipment is available
        if equipment.status != EquipmentStatus.AVAILABLE:
            return False
        
        # Check for overlapping bookings
        from app.models.booking import Booking
        overlapping = self.db.query(Booking).join(BookingItem).filter(
            BookingItem.equipment_id == equipment_id,
            Booking.status.in_([
                BookingStatus.CONFIRMED,
                BookingStatus.ACTIVE
            ]),
            Booking.end_date > start_date,
            Booking.start_date < end_date
        ).first()
        
        return overlapping is None
