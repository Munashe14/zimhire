from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class DashboardMetrics(BaseModel):
    total_equipment: int
    equipment_available: int
    equipment_rented_out: int
    equipment_under_maintenance: int
    active_bookings: int
    upcoming_bookings: int
    overdue_equipment: int
    open_disputes: int
    outstanding_invoices: int
    outstanding_amount_cents: int
    matched_payments_cents: int
    unmatched_payments_cents: int


class EquipmentUtilization(BaseModel):
    equipment_id: int
    equipment_name: str
    identification_number: str
    total_rental_days: int
    revenue_cents: int
    utilization_rate: float


class BookingReport(BaseModel):
    booking_id: int
    booking_reference: str
    client_name: str
    start_date: datetime
    end_date: datetime
    status: str
    total_amount_cents: int
    created_at: datetime


class RevenueReport(BaseModel):
    period_start: datetime
    period_end: datetime
    total_revenue_cents: int
    booking_count: int
    average_booking_value_cents: int
