"""
Seed database with sample data for development.
Run this after initializing the database.
"""
import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models import *
from app.models.user import UserRole
from app.models.equipment import EquipmentStatus
from app.models.booking import BookingStatus
from app.models.invoice import InvoiceStatus
from app.models.payment import PaymentStatus, PaymentMethod
from app.models.dispute import DisputeStatus
from app.models.alert import AlertType, AlertStatus


def seed_all():
    """Run all seed functions."""
    db = SessionLocal()
    
  

def seed_users(db):
    """Create sample users with different roles."""
    print("Seeding users...")
    
    users = [
        {
            "username": "admin",
            "email": "admin@zimhire.co.zw",
            "full_name": "System Administrator",
            "password": "Admin123!",
            "role": UserRole.ADMIN,
        },
        {
            "username": "booking_clerk",
            "email": "clerk@zimhire.co.zw",
            "full_name": "John Clerk",
            "password": "Clerk123!",
            "role": UserRole.BOOKING_CLERK,
        },
        {
            "username": "depot_supervisor",
            "email": "supervisor@zimhire.co.zw",
            "full_name": "Mary Supervisor",
            "password": "Supervisor123!",
            "role": UserRole.DEPOT_SUPERVISOR,
        },
        {
            "username": "ops_manager",
            "email": "manager@zimhire.co.zw",
            "full_name": "Peter Manager",
            "password": "Manager123!",
            "role": UserRole.OPERATIONS_MANAGER,
        },
        {
            "username": "client_user",
            "email": "client@example.com",
            "full_name": "Jane Client",
            "password": "Client123!",
            "role": UserRole.CLIENT,
        },
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)
    
    db.commit()
    print("Users seeded successfully!")


def seed_equipment_categories(db):
    """Create sample equipment categories."""
    print("Seeding equipment categories...")
    
    categories = [
        {"name": "Excavators", "description": "Heavy excavation equipment"},
        {"name": "Loaders", "description": "Material loading equipment"},
        {"name": "Compactors", "description": "Soil compaction equipment"},
        {"name": "Generators", "description": "Power generation equipment"},
        {"name": "Concrete Mixers", "description": "Concrete mixing equipment"},
    ]
    
    for cat_data in categories:
        existing = db.query(EquipmentCategory).filter(EquipmentCategory.name == cat_data["name"]).first()
        if not existing:
            category = EquipmentCategory(**cat_data)
            db.add(category)
    
    db.commit()
    print("Equipment categories seeded successfully!")


def seed_equipment(db):
    """Create sample equipment."""
    print("Seeding equipment...")
    
    categories = db.query(EquipmentCategory).all()
    if not categories:
        print("No categories found. Run equipment categories seed first.")
        return
    
    equipment_data = [
        {"name": "CAT 320 Excavator", "identification_number": "EXC-001", "category_id": categories[0].id, "daily_rate": 15000, "status": EquipmentStatus.AVAILABLE},
        {"name": "JCB 3CX Backhoe", "identification_number": "EXC-002", "category_id": categories[0].id, "daily_rate": 12000, "status": EquipmentStatus.AVAILABLE},
        {"name": "CAT 950H Wheel Loader", "identification_number": "LDR-001", "category_id": categories[1].id, "daily_rate": 10000, "status": EquipmentStatus.RENTED_OUT},
        {"name": "Volvo L120F Loader", "identification_number": "LDR-002", "category_id": categories[1].id, "daily_rate": 11000, "status": EquipmentStatus.AVAILABLE},
        {"name": "Bomag BW 213 Roller", "identification_number": "CMP-001", "category_id": categories[2].id, "daily_rate": 8000, "status": EquipmentStatus.UNDER_MAINTENANCE},
        {"name": "Wacker Neuson RD27", "identification_number": "CMP-002", "category_id": categories[2].id, "daily_rate": 5000, "status": EquipmentStatus.AVAILABLE},
        {"name": "Perkins 500kVA Generator", "identification_number": "GEN-001", "category_id": categories[3].id, "daily_rate": 7000, "status": EquipmentStatus.AVAILABLE},
        {"name": "Cummins 250kVA Generator", "identification_number": "GEN-002", "category_id": categories[3].id, "daily_rate": 5000, "status": EquipmentStatus.AVAILABLE},
        {"name": "Cementech 5 Mixer", "identification_number": "MIX-001", "category_id": categories[4].id, "daily_rate": 4000, "status": EquipmentStatus.AVAILABLE},
        {"name": "Quikrete 10 Mixer", "identification_number": "MIX-002", "category_id": categories[4].id, "daily_rate": 3500, "status": EquipmentStatus.AVAILABLE},
    ]
    
    for eq_data in equipment_data:
        existing = db.query(Equipment).filter(
            Equipment.identification_number == eq_data["identification_number"]
        ).first()
        if not existing:
            equipment = Equipment(**eq_data)
            db.add(equipment)
    
    db.commit()
    print("Equipment seeded successfully!")


def seed_clients(db):
    """Create sample clients."""
    print("Seeding clients...")
    
    clients = [
        {
            "full_name": "Construction Zimbabwe Ltd",
            "business_name": "Construction Zimbabwe Ltd",
            "phone_number": "+263771234567",
            "email": "info@constructionzw.co.zw",
            "address": "123 Harare Drive, Harare",
            "client_type": ClientType.BUSINESS,
        },
        {
            "full_name": "Tendai Chimedza",
            "phone_number": "+263712345678",
            "email": "tendai@example.com",
            "address": "456 Bindura Road, Harare",
            "client_type": ClientType.INDIVIDUAL,
        },
        {
            "full_name": "Build It Right Contractors",
            "business_name": "Build It Right Contractors",
            "phone_number": "+263773456789",
            "email": "builditright@example.com",
            "address": "789 Bulawayo Road, Harare",
            "client_type": ClientType.BUSINESS,
        },
    ]
    
    for client_data in clients:
        existing = db.query(Client).filter(Client.phone_number == client_data["phone_number"]).first()
        if not existing:
            client = Client(**client_data)
            db.add(client)
    
    db.commit()
    print("Clients seeded successfully!")


def seed_bookings(db):
    """Create sample bookings."""
    print("Seeding bookings...")
    
    clients = db.query(Client).all()
    equipment = db.query(Equipment).filter(Equipment.status == EquipmentStatus.AVAILABLE).all()
    users = db.query(User).filter(User.role == UserRole.BOOKING_CLERK).first()
    
    if not clients or not equipment or not users:
        print("Missing required data. Seed clients, equipment, and users first.")
        return
    
    now = datetime.utcnow()
    
    # Active booking
    booking1 = Booking(
        booking_reference=f"ZMH-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}",
        client_id=clients[0].id,
        created_by_user_id=users.id,
        start_date=now - timedelta(days=5),
        end_date=now + timedelta(days=5),
        status=BookingStatus.ACTIVE,
        total_amount=75000,  # 5 days * 15000 cents
        currency="USD",
        notes="Project at CBD construction site",
    )
    db.add(booking1)
    db.flush()
    
    booking_item1 = BookingItem(
        booking_id=booking1.id,
        equipment_id=equipment[0].id,
        daily_rate=15000,
        currency="USD",
    )
    db.add(booking_item1)
    
    # Completed booking
    booking2 = Booking(
        booking_reference=f"ZMH-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}",
        client_id=clients[1].id,
        created_by_user_id=users.id,
        start_date=now - timedelta(days=20),
        end_date=now - timedelta(days=15),
        status=BookingStatus.COMPLETED,
        total_amount=60000,
        currency="USD",
        notes="Weekend rental for home renovation",
    )
    db.add(booking2)
    db.flush()
    
    booking_item2 = BookingItem(
        booking_id=booking2.id,
        equipment_id=equipment[1].id,
        daily_rate=12000,
        currency="USD",
    )
    db.add(booking_item2)
    
    # Confirmed booking (upcoming)
    booking3 = Booking(
        booking_reference=f"ZMH-{datetime.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}",
        client_id=clients[2].id,
        created_by_user_id=users.id,
        start_date=now + timedelta(days=10),
        end_date=now + timedelta(days=20),
        status=BookingStatus.CONFIRMED,
        total_amount=200000,
        currency="USD",
        notes="Large construction project",
    )
    db.add(booking3)
    db.flush()
    
    booking_item3 = BookingItem(
        booking_id=booking3.id,
        equipment_id=equipment[2].id,
        daily_rate=10000,
        currency="USD",
    )
    db.add(booking_item3)
    
    db.commit()
    print("Bookings seeded successfully!")


def seed_inspections(db):
    """Create sample inspection records."""
    print("Seeding inspections...")
    
    bookings = db.query(Booking).all()
    supervisor = db.query(User).filter(User.role == UserRole.DEPOT_SUPERVISOR).first()
    
    if not bookings or not supervisor:
        print("Missing required data. Seed bookings and users first.")
        return
    
    # Dispatch inspection for active booking
    dispatch_record = ConditionRecord(
        booking_id=bookings[0].id,
        equipment_id=bookings[0].booking_items[0].equipment_id,
        inspection_type=InspectionType.DISPATCH,
        inspector_id=supervisor.id,
        condition="Excellent",
        notes="Equipment in perfect working condition",
        damage_flagged=0,
    )
    db.add(dispatch_record)
    
    # Return inspection for completed booking
    return_record = ConditionRecord(
        booking_id=bookings[1].id,
        equipment_id=bookings[1].booking_items[0].equipment_id,
        inspection_type=InspectionType.RETURN,
        inspector_id=supervisor.id,
        condition="Good",
        notes="Minor wear on tires, otherwise good",
        damage_flagged=0,
    )
    db.add(return_record)
    
    db.commit()
    print("Inspections seeded successfully!")


def seed_disputes(db):
    """Create sample damage dispute."""
    print("Seeding disputes...")
    
    bookings = db.query(Booking).filter(Booking.status == BookingStatus.COMPLETED).first()
    manager = db.query(User).filter(User.role == UserRole.OPERATIONS_MANAGER).first()
    
    if not bookings or not manager:
        print("Missing required data. Seed bookings and users first.")
        return
    
    dispute = DamageDispute(
        booking_id=bookings.id,
        equipment_id=bookings.booking_items[0].equipment_id,
        reviewer_id=manager.id,
        status=DisputeStatus.UNDER_REVIEW,
        damage_description="Scratches on excavator bucket and minor hydraulic leak",
        resolution_notes="Under investigation",
    )
    db.add(dispute)
    
    db.commit()
    print("Disputes seeded successfully!")


def seed_invoices_and_payments(db):
    """Create sample invoices and payments."""
    print("Seeding invoices and payments...")
    
    bookings = db.query(Booking).all()
    
    if not bookings:
        print("No bookings found. Seed bookings first.")
        return
    
    # Invoice for completed booking (paid)
    invoice1 = Invoice(
        invoice_number="INV-202610-1001",
        booking_id=bookings[1].id,
        client_id=bookings[1].client_id,
        issue_date=datetime.utcnow() - timedelta(days=15),
        due_date=datetime.utcnow() - timedelta(days=10),
        status=InvoiceStatus.PAID,
        subtotal_cents=60000,
        tax_cents=0,
        total_cents=60000,
        currency="USD",
    )
    db.add(invoice1)
    db.flush()
    
    payment1 = Payment(
        invoice_id=invoice1.id,
        payment_reference="ECO-123456789",
        provider_transaction_id="TXN-ABC123",
        payment_method=PaymentMethod.ECOCASH,
        amount_cents=60000,
        currency="USD",
        status=PaymentStatus.MATCHED,
        payment_date=datetime.utcnow() - timedelta(days=12),
        matched_date=datetime.utcnow() - timedelta(days=12),
        is_simulated=0,
    )
    db.add(payment1)
    
    # Invoice for active booking (outstanding)
    invoice2 = Invoice(
        invoice_number="INV-202610-1002",
        booking_id=bookings[0].id,
        client_id=bookings[0].client_id,
        issue_date=datetime.utcnow() - timedelta(days=5),
        due_date=datetime.utcnow() + timedelta(days=10),
        status=InvoiceStatus.ISSUED,
        subtotal_cents=75000,
        tax_cents=0,
        total_cents=75000,
        currency="USD",
    )
    db.add(invoice2)
    
    # Unmatched payment
    payment2 = Payment(
        payment_reference="ZIP-987654321",
        provider_transaction_id="TXN-XYZ789",
        payment_method=PaymentMethod.ZIPIT,
        amount_cents=50000,
        currency="USD",
        status=PaymentStatus.UNMATCHED,
        payment_date=datetime.utcnow() - timedelta(days=2),
        is_simulated=0,
    )
    db.add(payment2)
    
    db.commit()
    print("Invoices and payments seeded successfully!")


def seed_alerts(db):
    """Create sample alerts."""
    print("Seeding alerts...")
    
    active_bookings = db.query(Booking).filter(Booking.status == BookingStatus.ACTIVE).all()
    
    if not active_bookings:
        print("No active bookings found.")
        return
    
    # Overdue alert
    alert = Alert(
        alert_type=AlertType.OVERDUE_EQUIPMENT,
        booking_id=active_bookings[0].id,
        equipment_id=active_bookings[0].booking_items[0].equipment_id,
        message=f"Equipment {active_bookings[0].booking_items[0].equipment_id} overdue for booking {active_bookings[0].booking_reference}",
        status=AlertStatus.OPEN,
    )
    db.add(alert)
    
    db.commit()
    print("Alerts seeded successfully!")


def seed_all():
    """Run all seed functions."""
    db = SessionLocal()
    
    try:
        seed_users(db)
        seed_equipment_categories(db)
        seed_equipment(db)
        seed_clients(db)
        seed_bookings(db)
        seed_inspections(db)
        seed_disputes(db)
        seed_invoices_and_payments(db)
        seed_alerts(db)
        
        print("\n=== Database seeded successfully! ===")
        print("\nDemo credentials:")
        print("  Admin: admin / Admin123!")
        print("  Booking Clerk: booking_clerk / Clerk123!")
        print("  Depot Supervisor: depot_supervisor / Supervisor123!")
        print("  Operations Manager: ops_manager / Manager123!")
        print("  Client: client_user / Client123!")
        print("\nWARNING: These are development credentials only. Do not use in production!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
