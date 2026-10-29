from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List
from app.models.equipment import Equipment, EquipmentStatus
from app.models.booking import Booking, BookingStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus
from app.models.dispute import DamageDispute, DisputeStatus
from app.models.alert import Alert, AlertStatus
from app.schemas.report import (
    DashboardMetrics,
    EquipmentUtilization,
    BookingReport,
    RevenueReport,
)


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics for operations manager."""
        # Equipment counts
        total_equipment = self.db.query(Equipment).count()
        equipment_available = self.db.query(Equipment).filter(
            Equipment.status == EquipmentStatus.AVAILABLE
        ).count()
        equipment_rented_out = self.db.query(Equipment).filter(
            Equipment.status == EquipmentStatus.RENTED_OUT
        ).count()
        equipment_under_maintenance = self.db.query(Equipment).filter(
            Equipment.status == EquipmentStatus.UNDER_MAINTENANCE
        ).count()
        
        # Booking counts
        active_bookings = self.db.query(Booking).filter(
            Booking.status == BookingStatus.ACTIVE
        ).count()
        upcoming_bookings = self.db.query(Booking).filter(
            Booking.status == BookingStatus.CONFIRMED,
            Booking.start_date > datetime.utcnow()
        ).count()
        
        # Overdue equipment
        overdue_bookings = self.db.query(Booking).filter(
            Booking.status == BookingStatus.ACTIVE,
            Booking.end_date < datetime.utcnow()
        ).all()
        overdue_equipment = len(set(
            item.equipment_id for booking in overdue_bookings for item in booking.booking_items
        ))
        
        # Open disputes
        open_disputes = self.db.query(DamageDispute).filter(
            DamageDispute.status.in_([DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW])
        ).count()
        
        # Outstanding invoices
        outstanding_invoices = self.db.query(Invoice).filter(
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.OVERDUE])
        ).all()
        outstanding_amount = sum(
            inv.total_cents - self._calculate_invoice_paid(inv.id)
            for inv in outstanding_invoices
        )
        
        # Payments
        matched_payments = self.db.query(Payment).filter(
            Payment.status == PaymentStatus.MATCHED
        ).all()
        matched_amount = sum(p.amount_cents for p in matched_payments)
        
        unmatched_payments = self.db.query(Payment).filter(
            Payment.status == PaymentStatus.UNMATCHED
        ).all()
        unmatched_amount = sum(p.amount_cents for p in unmatched_payments)
        
        return DashboardMetrics(
            total_equipment=total_equipment,
            equipment_available=equipment_available,
            equipment_rented_out=equipment_rented_out,
            equipment_under_maintenance=equipment_under_maintenance,
            active_bookings=active_bookings,
            upcoming_bookings=upcoming_bookings,
            overdue_equipment=overdue_equipment,
            open_disputes=open_disputes,
            outstanding_invoices=len(outstanding_invoices),
            outstanding_amount_cents=outstanding_amount,
            matched_payments_cents=matched_amount,
            unmatched_payments_cents=unmatched_amount,
        )

    def _calculate_invoice_paid(self, invoice_id: int) -> int:
        """Calculate paid amount for an invoice."""
        payments = self.db.query(Payment).filter(
            Payment.invoice_id == invoice_id,
            Payment.status == PaymentStatus.MATCHED
        ).all()
        return sum(p.amount_cents for p in payments)

    def get_equipment_utilization(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[EquipmentUtilization]:
        """Get equipment utilization report for a period."""
        equipment_list = self.db.query(Equipment).all()
        utilization_data = []
        
        for equipment in equipment_list:
            # Get completed bookings for this equipment in the period
            from app.models.booking import BookingItem
            bookings = self.db.query(Booking).join(BookingItem).filter(
                BookingItem.equipment_id == equipment.id,
                Booking.status == BookingStatus.COMPLETED,
                Booking.end_date >= start_date,
                Booking.start_date <= end_date
            ).all()
            
            total_rental_days = 0
            revenue = 0
            
            for booking in bookings:
                days = (booking.end_date - booking.start_date).days
                if days < 1:
                    days = 1
                total_rental_days += days
                revenue += booking.total_amount_cents
            
            # Calculate utilization rate (days rented / days in period)
            period_days = (end_date - start_date).days
            utilization_rate = (total_rental_days / period_days * 100) if period_days > 0 else 0
            
            utilization_data.append(EquipmentUtilization(
                equipment_id=equipment.id,
                equipment_name=equipment.name,
                identification_number=equipment.identification_number,
                total_rental_days=total_rental_days,
                revenue_cents=revenue,
                utilization_rate=round(utilization_rate, 2),
            ))
        
        return utilization_data

    def get_booking_report(
        self,
        start_date: datetime,
        end_date: datetime,
        status: BookingStatus = None
    ) -> List[BookingReport]:
        """Get booking report for a period."""
        query = self.db.query(Booking).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        )
        
        if status:
            query = query.filter(Booking.status == status)
        
        bookings = query.order_by(Booking.created_at.desc()).all()
        
        report_data = []
        for booking in bookings:
            report_data.append(BookingReport(
                booking_id=booking.id,
                booking_reference=booking.booking_reference,
                client_name=booking.client.full_name if booking.client else "Unknown",
                start_date=booking.start_date,
                end_date=booking.end_date,
                status=booking.status.value,
                total_amount_cents=booking.total_amount,
                created_at=booking.created_at,
            ))
        
        return report_data

    def get_revenue_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> RevenueReport:
        """Get revenue report for a period."""
        # Get completed bookings in the period
        bookings = self.db.query(Booking).filter(
            Booking.status == BookingStatus.COMPLETED,
            Booking.end_date >= start_date,
            Booking.end_date <= end_date
        ).all()
        
        total_revenue = sum(b.total_amount for b in bookings)
        booking_count = len(bookings)
        average_value = total_revenue / booking_count if booking_count > 0 else 0
        
        return RevenueReport(
            period_start=start_date,
            period_end=end_date,
            total_revenue_cents=total_revenue,
            booking_count=booking_count,
            average_booking_value_cents=int(average_value),
        )
