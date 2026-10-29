from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List
from pathlib import Path
import uuid
from app.models.inspection import ConditionRecord, ConditionPhoto, InspectionType
from app.models.booking import Booking
from app.models.equipment import Equipment
from app.schemas.inspection import ConditionRecordCreate, ConditionRecordUpdate
from app.core.config import settings


class InspectionService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_file(self, file: UploadFile) -> int:
        """Validate uploaded file type and size. Returns file size."""
        if file.content_type not in settings.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_FILE_TYPES)}",
            )
        
        # Read file to check size
        content = file.file.read()
        file_size = len(content)
        file.file.seek(0)  # Reset file pointer
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE} bytes",
            )
        
        return file_size

    def _save_uploaded_file(self, file: UploadFile, file_size: int) -> tuple:
        """Save uploaded file and return the file path and size."""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return str(file_path), file_size

    def create_condition_record(
        self,
        record_data: ConditionRecordCreate,
        inspector_id: int,
        photos: Optional[List[UploadFile]] = None
    ) -> ConditionRecord:
        """Create a new condition record with optional photos."""
        # Verify booking exists
        booking = self.db.query(Booking).filter(Booking.id == record_data.booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        
        # Verify equipment exists
        equipment = self.db.query(Equipment).filter(Equipment.id == record_data.equipment_id).first()
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipment not found",
            )
        
        # Verify equipment is in the booking
        from app.models.booking import BookingItem
        booking_item = self.db.query(BookingItem).filter(
            BookingItem.booking_id == record_data.booking_id,
            BookingItem.equipment_id == record_data.equipment_id
        ).first()
        if not booking_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Equipment not found in this booking",
            )
        
        # Create condition record
        record = ConditionRecord(
            booking_id=record_data.booking_id,
            equipment_id=record_data.equipment_id,
            inspection_type=record_data.inspection_type,
            inspector_id=inspector_id,
            condition=record_data.condition,
            notes=record_data.notes,
            damage_flagged=1 if record_data.damage_flagged else 0,
        )
        self.db.add(record)
        self.db.flush()  # Get record ID
        
        # Save photos if provided
        if photos:
            for photo in photos:
                file_size = self._validate_file(photo)
                file_path, _ = self._save_uploaded_file(photo, file_size)
                
                photo_record = ConditionPhoto(
                    condition_record_id=record.id,
                    file_path=file_path,
                    file_name=photo.filename,
                    file_size=file_size,
                    mime_type=photo.content_type,
                )
                self.db.add(photo_record)
        
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_condition_record(self, record_id: int) -> ConditionRecord:
        """Get a condition record by ID."""
        record = self.db.query(ConditionRecord).filter(ConditionRecord.id == record_id).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Condition record not found",
            )
        return record

    def list_condition_records(
        self,
        skip: int = 0,
        limit: int = 100,
        booking_id: int = None,
        equipment_id: int = None,
        inspection_type: InspectionType = None
    ) -> tuple:
        """List condition records with optional filters."""
        query = self.db.query(ConditionRecord)
        
        if booking_id:
            query = query.filter(ConditionRecord.booking_id == booking_id)
        if equipment_id:
            query = query.filter(ConditionRecord.equipment_id == equipment_id)
        if inspection_type:
            query = query.filter(ConditionRecord.inspection_type == inspection_type)
        
        query = query.order_by(ConditionRecord.inspection_date.desc())
        
        total = query.count()
        records = query.offset(skip).limit(limit).all()
        return records, total

    def compare_inspections(self, booking_id: int, equipment_id: int) -> dict:
        """Compare dispatch and return inspections for a booking."""
        dispatch = self.db.query(ConditionRecord).filter(
            ConditionRecord.booking_id == booking_id,
            ConditionRecord.equipment_id == equipment_id,
            ConditionRecord.inspection_type == InspectionType.DISPATCH
        ).first()
        
        return_inspection = self.db.query(ConditionRecord).filter(
            ConditionRecord.booking_id == booking_id,
            ConditionRecord.equipment_id == equipment_id,
            ConditionRecord.inspection_type == InspectionType.RETURN
        ).first()
        
        damage_detected = False
        if return_inspection and return_inspection.damage_flagged:
            damage_detected = True
        
        return {
            "dispatch": dispatch,
            "return_inspection": return_inspection,
            "damage_detected": damage_detected,
        }

    def update_condition_record(
        self,
        record_id: int,
        record_data: ConditionRecordUpdate
    ) -> ConditionRecord:
        """Update a condition record."""
        record = self.get_condition_record(record_id)
        
        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "damage_flagged":
                setattr(record, field, 1 if value else 0)
            else:
                setattr(record, field, value)
        
        self.db.commit()
        self.db.refresh(record)
        return record
