from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, equipment, client, booking, inspection, dispute, invoice, payment, alert, report

app = FastAPI(
    title="ZimHire Equipment Rental Management System",
    description="API for managing equipment rentals, bookings, inspections, and payments",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(equipment.router)
app.include_router(client.router)
app.include_router(booking.router)
app.include_router(inspection.router)
app.include_router(dispute.router)
app.include_router(invoice.router)
app.include_router(payment.router)
app.include_router(alert.router)
app.include_router(report.router)


@app.get("/")
def root():
    return {
        "message": "ZimHire Equipment Rental Management System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
