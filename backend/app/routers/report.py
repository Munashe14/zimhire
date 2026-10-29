from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.deps import require_operations_manager, require_admin
from app.schemas.report import (
    DashboardMetrics,
    EquipmentUtilization,
    BookingReport,
    RevenueReport,
)
from app.services.report_service import ReportService
from app.models.booking import BookingStatus
from app.models.user import User

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get dashboard metrics (operations manager or admin)."""
    service = ReportService(db)
    return service.get_dashboard_metrics()


@router.get("/equipment-utilization", response_model=list[EquipmentUtilization])
def get_equipment_utilization(
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get equipment utilization report (operations manager or admin)."""
    service = ReportService(db)
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    return service.get_equipment_utilization(start_dt, end_dt)


@router.get("/bookings", response_model=list[BookingReport])
def get_booking_report(
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    status: Optional[BookingStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get booking report (operations manager or admin)."""
    service = ReportService(db)
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    return service.get_booking_report(start_dt, end_dt, status)


@router.get("/revenue", response_model=RevenueReport)
def get_revenue_report(
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operations_manager)
):
    """Get revenue report (operations manager or admin)."""
    service = ReportService(db)
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    return service.get_revenue_report(start_dt, end_dt)
