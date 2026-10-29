from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from datetime import datetime
from app.models.alert import Alert, AlertType, AlertStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert."""
        # Check for duplicate open alert
        if alert_data.booking_id and alert_data.equipment_id:
            existing = self.db.query(Alert).filter(
                Alert.alert_type == alert_data.alert_type,
                Alert.booking_id == alert_data.booking_id,
                Alert.equipment_id == alert_data.equipment_id,
                Alert.status == AlertStatus.OPEN
            ).first()
            if existing:
                return existing  # Return existing alert instead of creating duplicate
        
        alert = Alert(
            alert_type=alert_data.alert_type,
            booking_id=alert_data.booking_id,
            equipment_id=alert_data.equipment_id,
            message=alert_data.message,
            status=AlertStatus.OPEN,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_alert(self, alert_id: int) -> Alert:
        """Get an alert by ID."""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )
        return alert

    def list_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        alert_type: AlertType = None,
        status: AlertStatus = None
    ) -> Tuple[list[Alert], int]:
        """List alerts with optional filters."""
        query = self.db.query(Alert)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        if status:
            query = query.filter(Alert.status == status)
        
        query = query.order_by(Alert.created_at.desc())
        
        total = query.count()
        alerts = query.offset(skip).limit(limit).all()
        return alerts, total

    def acknowledge_alert(self, alert_id: int, user_id: int) -> Alert:
        """Acknowledge an alert."""
        alert = self.get_alert(alert_id)
        
        if alert.status != AlertStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Alert is not in OPEN status",
            )
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by_id = user_id
        alert.acknowledged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def resolve_alert(self, alert_id: int) -> Alert:
        """Resolve an alert."""
        alert = self.get_alert(alert_id)
        
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def check_overdue_equipment(self) -> list[Alert]:
        """Check for overdue equipment and create alerts."""
        now = datetime.utcnow()
        
        # Find active bookings that are overdue
        overdue_bookings = self.db.query(Booking).filter(
            Booking.status == BookingStatus.ACTIVE,
            Booking.end_date < now
        ).all()
        
        alerts_created = []
        for booking in overdue_bookings:
            for item in booking.booking_items:
                # Check if alert already exists
                existing = self.db.query(Alert).filter(
                    Alert.alert_type == AlertType.OVERDUE_EQUIPMENT,
                    Alert.booking_id == booking.id,
                    Alert.equipment_id == item.equipment_id,
                    Alert.status == AlertStatus.OPEN
                ).first()
                
                if not existing:
                    from app.schemas.alert import AlertCreate
                    alert_data = AlertCreate(
                        alert_type=AlertType.OVERDUE_EQUIPMENT,
                        booking_id=booking.id,
                        equipment_id=item.equipment_id,
                        message=f"Equipment overdue for booking {booking.booking_reference}. Expected return: {booking.end_date}"
                    )
                    alert = self.create_alert(alert_data)
                    alerts_created.append(alert)
        
        return alerts_created
