# ZimHire ERMS - Backend API

FastAPI backend for the ZimHire Equipment Rental Management System.

## Prerequisites

- Python 3.13 or higher
- pip (Python package manager)

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv13
```

3. Activate the virtual environment:

**Windows:**
```bash
.\venv13\Scripts\activate
```

**Linux/Mac:**
```bash
source venv13/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
DATABASE_URL=sqlite:///./zimhire.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Database Setup

This project uses SQLite by default, so no Docker services or external PostgreSQL installation are required.

### Initialize Database

1. Create database tables:
```bash
cd backend
python scripts/init_db.py
```

2. (Optional) Seed with sample data:
```bash
python scripts/seed_db.py
```

### Initialize Database

1. Create database tables:
```bash
cd backend
python scripts/init_db.py
```

2. (Optional) Seed with sample data:
```bash
python scripts/seed_db.py
```

## Running the Backend

Start the FastAPI development server:

```bash
cd backend
.\venv13\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/users/me` - Get current user
- `POST /api/auth/users` - Create user (admin only)
- `GET /api/auth/users` - List users (admin only)
- `GET /api/auth/users/{id}` - Get user (admin only)
- `PUT /api/auth/users/{id}` - Update user (admin only)

### Equipment
- `POST /api/equipment/categories` - Create category (admin only)
- `GET /api/equipment/categories` - List categories (staff only)
- `GET /api/equipment/categories/{id}` - Get category (staff only)
- `PUT /api/equipment/categories/{id}` - Update category (admin only)
- `POST /api/equipment` - Create equipment (admin only)
- `GET /api/equipment` - List equipment (staff only)
- `GET /api/equipment/{id}` - Get equipment (staff only)
- `PUT /api/equipment/{id}` - Update equipment (admin only)
- `GET /api/equipment/{id}/availability` - Check availability (staff only)

### Clients
- `POST /api/clients` - Create client (booking clerk or admin)
- `GET /api/clients` - List clients (booking clerk or admin)
- `GET /api/clients/{id}` - Get client (booking clerk or admin)
- `PUT /api/clients/{id}` - Update client (booking clerk or admin)

### Bookings
- `POST /api/bookings/check-availability` - Check availability (booking clerk or admin)
- `POST /api/bookings` - Create booking (booking clerk or admin)
- `GET /api/bookings` - List bookings (booking clerk or admin)
- `GET /api/bookings/{id}` - Get booking (booking clerk or admin)
- `PUT /api/bookings/{id}` - Update booking (booking clerk or admin)

### Inspections
- `POST /api/inspections` - Create inspection record (depot supervisor or admin)
- `GET /api/inspections` - List inspections (depot supervisor or admin)
- `GET /api/inspections/{id}` - Get inspection (depot supervisor or admin)
- `GET /api/inspections/compare/{booking_id}/{equipment_id}` - Compare inspections (depot supervisor or admin)
- `PUT /api/inspections/{id}` - Update inspection (depot supervisor or admin)

### Damage Disputes
- `POST /api/disputes` - Create dispute (operations manager or admin)
- `GET /api/disputes` - List disputes (operations manager or admin)
- `GET /api/disputes/{id}` - Get dispute (operations manager or admin)
- `PUT /api/disputes/{id}` - Update dispute (operations manager or admin)

### Invoices
- `POST /api/invoices` - Create invoice (booking clerk or admin)
- `GET /api/invoices` - List invoices (booking clerk or admin)
- `GET /api/invoices/{id}` - Get invoice (booking clerk or admin)
- `PUT /api/invoices/{id}` - Update invoice (booking clerk or admin)
- `POST /api/invoices/{id}/issue` - Issue invoice (booking clerk or admin)

### Payments
- `POST /api/payments` - Create payment (booking clerk or admin)
- `GET /api/payments` - List payments (booking clerk or admin)
- `GET /api/payments/unmatched` - Get unmatched payments (operations manager or admin)
- `GET /api/payments/{id}` - Get payment (booking clerk or admin)
- `PUT /api/payments/{id}` - Update payment (booking clerk or admin)
- `POST /api/payments/match` - Match payment to invoice (operations manager or admin)

### Alerts
- `POST /api/alerts` - Create alert (admin only)
- `GET /api/alerts` - List alerts (staff only)
- `GET /api/alerts/{id}` - Get alert (staff only)
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert (staff only)
- `POST /api/alerts/{id}/resolve` - Resolve alert (staff only)
- `POST /api/alerts/check-overdue` - Check for overdue equipment (admin only)

### Reports
- `GET /api/reports/dashboard` - Get dashboard metrics (operations manager or admin)
- `GET /api/reports/equipment-utilization` - Get equipment utilization (operations manager or admin)
- `GET /api/reports/bookings` - Get booking report (operations manager or admin)
- `GET /api/reports/revenue` - Get revenue report (operations manager or admin)

## User Roles

- **Admin**: Full system access, user management, system configuration
- **Booking Clerk**: Client management, booking creation, invoice generation
- **Depot Supervisor**: Equipment dispatch/return, inspections, damage reporting
- **Operations Manager**: Dashboard, reports, dispute resolution, payment reconciliation
- **Client**: View availability, submit booking requests, view invoices (if enabled)

## Demo Credentials (Development Only)

⚠️ **WARNING**: These are development credentials. Do not use in production!

- **Admin**: `admin` / `Admin123!`
- **Booking Clerk**: `booking_clerk` / `Clerk123!`
- **Depot Supervisor**: `depot_supervisor` / `Supervisor123!`
- **Operations Manager**: `ops_manager` / `Manager123!`
- **Client**: `client_user` / `Client123!`

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

> SQLite is used for local development, so the migration files should be tested against the local file database.

## File Uploads

- Upload directory: `uploads/` (created automatically)
- Allowed file types: JPEG, PNG, GIF
- Maximum file size: 5MB
- Files are stored on the local filesystem

## Payment Integration

The system includes a sandbox/simulated payment adapter for development. To integrate with real payment providers:

1. Implement the payment provider adapter interface
2. Add provider credentials to `.env`
3. Update `PAYMENT_ADAPTER` setting to `live`
4. Implement webhook verification for payment notifications

Current status: Sandbox mode only - payments are simulated for testing.

## Security Features

- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- Role-based access control enforced on all endpoints
- File upload validation (type and size)
- SQL injection prevention through ORM
- CORS configuration
- Environment-based configuration

## Testing

Run backend tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Database Connection Error
- Check that `DATABASE_URL` in `.env` points to the local SQLite file
- Ensure the backend is being started from the project directory or that the SQLite file path resolves correctly
- If needed, delete the SQLite file and re-run `python scripts/init_db.py`

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change port in uvicorn command: `--port 8001`
- Or stop the process using port 8000

## License

Proprietary - ZimHire Equipment Rentals
