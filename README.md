# ZimHire Equipment Rental Management System

A comprehensive web-based system for managing equipment rentals, bookings, inspections, and payments for ZimHire Equipment Rentals in Harare, Zimbabwe.

## Project Status

### ✅ Completed (Backend API)

The backend API is fully implemented with all core functionality:

- **Authentication & Authorization**: JWT-based auth with role-based access control
- **User Management**: Admin, Booking Clerk, Depot Supervisor, Operations Manager, Client roles
- **Equipment Management**: Categories, equipment records, status tracking
- **Client Management**: Individual and business clients
- **Booking System**: Availability checking, conflict prevention, booking lifecycle
- **Inspections**: Dispatch and return inspections with photo uploads
- **Damage Disputes**: Dispute creation, review, and resolution workflow
- **Invoices**: Invoice generation, status tracking, payment reconciliation
- **Payments**: Recording, matching, and reconciliation (sandbox mode)
- **Alerts**: Overdue equipment detection and alert management
- **Reports**: Dashboard metrics, equipment utilization, booking and revenue reports
- **Seed Data**: Comprehensive sample data for development

### 🚧 In Progress / Future Work

- **Frontend Implementation**: React + TypeScript + Vite application
- **Comprehensive Testing**: Unit tests, integration tests, E2E tests
- **Live Payment Integration**: EcoCash and ZIPIT integration
- **Background Tasks**: Scheduled overdue checks via APScheduler
- **Offline Support**: PWA with offline capabilities (documented limitation)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM (no Docker required)
- **Authentication**: JWT with bcrypt password hashing
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **Migrations**: Alembic

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **State**: Local component state with browser storage

### Development
- **Database**: SQLite file-based storage
- **Environment**: Environment variables for configuration
- **Version Control**: Git

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+

### Backend Setup

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create or reuse the Python 3.13 virtual environment**:
```bash
py -3.13 -m venv venv313
.\venv313\Scripts\activate  # Windows
# or
source venv313/bin/activate  # Linux/Mac
```

> Use Python 3.13 for this project. The earlier 3.14 environment caused dependency incompatibilities with `pydantic` and `pydantic-core`.

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment** (optional):
```bash
copy .env.example .env
# Edit .env with your settings if needed
```

5. **Initialize the SQLite database**:
```bash
python scripts/init_db.py
python scripts/seed_db.py  # Optional: add sample data
```

6. **Run the API**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

7. **If port 8000 is in use, start on another port**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

8. **Access the API**:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Demo Credentials (Development Only)

⚠️ **Do not use these in production!**

- **Admin**: `admin` / `Admin123!`
- **Booking Clerk**: `booking_clerk` / `Clerk123!`
- **Depot Supervisor**: `depot_supervisor` / `Supervisor123!`
- **Operations Manager**: `ops_manager` / `Manager123!`
- **Client**: `client_user` / `Client123!`

## Project Structure

```
zimhire-erms/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── routers/        # API endpoints
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts
│   ├── uploads/            # File upload directory
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
├── docs/                   # Documentation
├── docker-compose.yml      # Legacy container config (not required for SQLite)
└── README.md              # This file
```

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs when the backend is running.

### Key Endpoints

- **Authentication**: `/api/auth/*`
- **Equipment**: `/api/equipment/*`
- **Clients**: `/api/clients/*`
- **Bookings**: `/api/bookings/*`
- **Inspections**: `/api/inspections/*`
- **Disputes**: `/api/disputes/*`
- **Invoices**: `/api/invoices/*`
- **Payments**: `/api/payments/*`
- **Alerts**: `/api/alerts/*`
- **Reports**: `/api/reports/*`

See `backend/README.md` for detailed API documentation.

## Database Schema

The database includes the following entities:

- **users**: User accounts with roles
- **clients**: Client information
- **equipment_categories**: Equipment categories
- **equipment**: Equipment inventory
- **bookings**: Rental bookings
- **booking_items**: Equipment items per booking
- **condition_records**: Inspection records
- **condition_photos**: Inspection photos
- **damage_disputes**: Damage dispute records
- **invoices**: Billing invoices
- **payments**: Payment records
- **alerts**: System alerts
- **audit_log**: Audit trail

All monetary values are stored in cents (integers) to avoid floating-point precision issues.

## Security Features

- ✅ Server-side validation on all endpoints
- ✅ Secure password hashing (bcrypt)
- ✅ Role-based permissions enforced on backend
- ✅ JWT access tokens (15-minute expiry)
- ✅ JWT refresh tokens (7-day expiry)
- ✅ File upload validation (type and size)
- ✅ SQL injection prevention (ORM)
- ✅ CORS configuration
- ✅ Environment-based configuration

## Known Limitations

1. **Payment Integration**: Currently in sandbox mode only. Live EcoCash and ZIPIT integration requires:
   - Official API credentials
   - Webhook endpoint implementation
   - Signature verification
   - Production testing

2. **Offline Support**: Initial version is online-only. The depot has intermittent connectivity, so offline support should be prioritized in Phase 2.

3. **Notifications**: In-app alerts are implemented. SMS, email, and push notifications require external service configuration.

4. **Background Tasks**: Overdue checks require manual API call. Scheduled background tasks via APScheduler should be implemented.

5. **Frontend**: A React dashboard has been implemented for login and equipment monitoring against the SQLite-backed API.

## Testing

Backend tests should be added using pytest:
```bash
cd backend
pytest
```

Test coverage should include:
- Authentication and authorization
- Booking conflict prevention
- Concurrent booking attempts
- Payment idempotency
- Financial calculations
- Role-based access enforcement

## Deployment Considerations

### Production Checklist

- [ ] Change SECRET_KEY to a strong random value
- [ ] Use a production-ready SQLite or external database if needed
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Disable debug mode
- [ ] Use production payment credentials
- [ ] Remove seed data from production

### Database Backup

```bash
# Backup
cp backend/zimhire.db backend/zimhire_backup.db

# Restore
cp backend/zimhire_backup.db backend/zimhire.db
```

## Documentation

- `backend/README.md` - Backend API documentation
- `docs/STATE_TRANSITIONS.md` - State transition rules
- `IMPLEMENTATION_PLAN.md` - Original implementation plan

## License

Proprietary - ZimHire Equipment Rentals

## Support

For issues or questions, please contact the development team.

---

**Note**: The backend now runs with SQLite for local development and the React frontend is connected to the live API for login and equipment monitoring.
