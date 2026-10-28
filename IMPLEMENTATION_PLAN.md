# ZimHire Equipment Rental Management System - Implementation Plan

## Phase 1: Repository Inspection and Implementation Plan

### Current State
- **Repository Status**: New project (no existing code)
- **Documentation**: Comprehensive requirements specification provided in prompt
- **Location**: C:\Users\Whispers95\Desktop\MyProjects\zimhire-erms

### Technology Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Router, React Hook Form, Recharts
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, JWT auth
- **Database**: PostgreSQL
- **Testing**: Pytest, Vitest, React Testing Library, Playwright
- **Deployment**: Docker Compose, Git, Environment variables

### Implementation Priority

#### Phase 2: Architecture and Database (Priority: Critical)
1. Define database schema with all entities
2. Create Alembic migrations
3. Define role-permission matrix
4. Define state transition rules
5. Create Docker Compose configuration

#### Phase 3: Backend Implementation (Priority: Critical)
1. Authentication and authorization (JWT, role-based)
2. User management
3. Equipment and category management
4. Client management
5. Availability checking and booking creation (with conflict prevention)
6. Dispatch and return inspections
7. Damage dispute management
8. Invoice generation and payment reconciliation
9. Overdue alerts and background tasks
10. Management reports
11. Backend tests

#### Phase 4: Frontend Implementation (Priority: Critical)
1. Project setup with Vite, TypeScript, Tailwind
2. Authentication pages (login, logout)
3. Role-aware layouts and navigation
4. Equipment management screens
5. Client management screens
6. Availability search and booking workflow
7. Inspection recording screens
8. Damage dispute screens
9. Invoice and payment screens
10. Overdue alerts dashboard
11. Management dashboard and reports
12. Frontend tests

#### Phase 5: Integration and QA (Priority: Critical)
1. End-to-end workflow testing
2. Role-based access verification
3. Booking conflict prevention verification
4. Payment idempotency verification
5. Financial calculation verification
6. Database migration testing
7. Seed data testing

#### Phase 6: Delivery and Documentation (Priority: Critical)
1. Complete README with setup instructions
2. Environment variable templates
3. Database backup/restore documentation
4. API documentation
5. Role permissions documentation
6. Seed data script
7. Known limitations documentation

### Key Technical Decisions

#### Database Schema
- Use decimal(10,2) for all monetary fields
- Use timestamp with timezone for all date fields
- Implement exclusion constraints for booking conflict prevention
- Foreign key cascades: cascade for audit, restrict for financial records

#### Authentication
- JWT access tokens (15-minute expiry)
- Refresh tokens (7-day expiry)
- bcrypt password hashing
- Role-based permissions enforced on all endpoints

#### Booking Conflict Prevention
- Database-level exclusion constraint on equipment_id + date range
- SERIALIZABLE isolation level for booking transactions
- Retry logic for concurrent booking attempts

#### Payment Integration
- Adapter pattern for payment providers
- Sandbox/simulated provider for development
- Clear distinction between simulated and real payments
- Idempotent payment processing

#### File Uploads
- Validate file type (images only)
- Limit file size (max 5MB)
- Store file metadata in database
- Store files in dedicated uploads directory

#### Offline Support
- Initial version: online-only (to ensure core functionality)
- Document limitation in Phase 6
- Design for future offline extension

### Risk Mitigation
- Use PostgreSQL exclusion constraints to prevent double bookings
- Implement comprehensive validation on both frontend and backend
- Use database transactions for financial operations
- Write tests for critical business logic
- Document all assumptions and limitations

### Success Criteria
See Acceptance Criteria in the main requirements document.
