from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.deps import require_staff, require_admin
from app.schemas.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertListResponse,
)
from app.services.alert_service import AlertService
from app.models.alert import AlertType, AlertStatus
from app.models.user import User

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new alert (admin only)."""
    service = AlertService(db)
    return service.create_alert(alert_data)


@router.get("", response_model=AlertListResponse)
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    alert_type: Optional[AlertType] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """List alerts with optional filters (staff only)."""
    service = AlertService(db)
    alerts, total = service.list_alerts(
        skip=skip,
        limit=limit,
        alert_type=alert_type,
        status=status
    )
    return AlertListResponse(
        items=alerts,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Get an alert by ID (staff only)."""
    service = AlertService(db)
    return service.get_alert(alert_id)


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Acknowledge an alert (staff only)."""
    service = AlertService(db)
    return service.acknowledge_alert(alert_id, current_user.id)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff)
):
    """Resolve an alert (staff only)."""
    service = AlertService(db)
    return service.resolve_alert(alert_id)


@router.post("/check-overdue")
def check_overdue_equipment(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Check for overdue equipment and create alerts (admin only)."""
    service = AlertService(db)
    alerts = service.check_overdue_equipment()
    return {"count": len(alerts), "alerts_created": [AlertResponse.model_validate(a) for a in alerts]}
