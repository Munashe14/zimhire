# ZimHire Equipment Rental System: Add Role-Based Data Entry and Filtering

## Context

This is the ZimHire Equipment Rentals management system (FastAPI + SQLAlchemy + PostgreSQL backend, React + Vite + TailwindCSS frontend). Right now every module (Equipment, Bookings, Inspections, Disputes, Payments, Reports, Administration) only **displays** data. There is no way to **create or edit** records from the UI, and lists cannot be **filtered**.

Your job: first audit the existing code, then add the missing create/edit/action features and filtering, each restricted to the correct role. Do not rewrite what already works. Extend it.

## Step 0: Audit first (do not code yet)

1. Read the backend: models, schemas, routers, services, auth/RBAC dependencies.
2. Read the frontend: routes, pages, API client, auth context, menu component.
3. Produce a short table: for each module, which endpoints exist (GET/POST/PUT/PATCH/DELETE) and which UI forms exist.
4. List the gaps against the spec below, then implement in the order given. Ask me only if something is truly ambiguous.

## Roles (users.role): `clerk`, `supervisor`, `manager`, `client`

Enforce permissions **on the server for every endpoint** (FastAPI dependency such as `require_roles(...)`), and also hide the matching menu items and buttons in the React UI. Hiding in the UI alone is not enough.

| Module | Clerk | Supervisor | Manager | Client (portal) |
|---|---|---|---|---|
| Dashboard | Yes | Yes | Yes | No |
| Bookings | Create, edit own pending, cancel, list all | View only | Full | Own bookings only (view, request) |
| Clients | Create, edit, list | View | Full | Own profile only |
| Equipment | View only | Create, edit, change status | Full (incl. rates, categories, deactivate) | No |
| Inspections | View only | Create dispatch/return inspections + upload photos | Full view | No |
| Damage disputes | View only | Raise a dispute | Raise + resolve | No |
| Payments / invoices | Invoices only (view, print) | No | Full (record manual payment, match, reconcile) | Own invoices only |
| Reports | No | Overdue report only | All reports | No |
| Administration (users, audit log) | No | No | Yes | No |

## Features to add (who enters what)

### 1. Equipment and categories (Manager and Supervisor)
- **Manager**: CRUD on `equipment_categories`. CRUD on `equipment` (asset_tag, name, category, daily_rate, description). Deactivate instead of hard delete if the item has booking history.
- **Supervisor**: add/edit equipment and change `status` (available, rented, maintenance, returned). Cannot change `daily_rate`.
- Form: "Add / Edit Equipment" with the validation rules below.

### 2. Clients (Clerk and Manager)
- Create/edit `clients` (client_type corporate|individual, name, contact_person, phone, email, address).
- Phone format `+263 7X XXX XXXX`; phone is also used to match mobile money payments, so it must be normalised before saving.

### 3. Bookings (Clerk and Manager; Client for own)
- "New Booking" form: select client (or create inline), start/end dates, add one or more equipment items.
- The **Confirm button stays disabled until an availability check for those dates succeeds**. Re-check on the server at submit time (no double booking, handle race conditions with a transaction/locking).
- On confirm: create `bookings` + `booking_items` (snapshot `daily_rate`), calculate `total_amount`, auto-create the `invoice` (unique `invoice_number`), set `created_by` from the logged-in user, write an audit log entry.
- Clerk can edit/cancel pending bookings. Manager can edit/cancel any. Supervisor sees read-only.
- Client portal: can request a booking and see only their own (server-side filter by the client linked to `users.user_id`).

### 4. Dispatch and return inspections (Supervisor)
- "Equipment Inspection" form tied to a `booking_item`: inspection_type (dispatch|return), rating (good|fair|damaged), notes, **at least one photo** (JPEG/PNG, max 5 MB, renamed to a generated filename, stored outside the web root).
- Dispatch inspection sets booking status to `active` and equipment status to `rented`.
- Return inspection sets `booking_items.returned_at`, equipment status to `returned` then `available` (or `maintenance` if damaged), and completes the booking when all items are back.
- A `damaged` return rating automatically raises a damage dispute (status `open`) and an alert.

### 5. Damage disputes (Supervisor raises, Manager resolves)
- Supervisor can raise a dispute manually. Manager can add `estimated_cost`, write `resolution_notes`, and mark it `resolved` (sets `resolved_at`).
- Dispute detail page shows all linked condition records and photos.

### 6. Payments (Manager; Clerk views invoices)
- Manager: "Record / Match Payment" form for payments the system could not auto-match: provider (ecocash|zipit), transaction_ref (unique per provider), payer_phone, amount, currency, and the invoice to match. Sets `match_status = manual`, updates invoice status (unpaid / part-paid / paid).
- Unmatched payments appear in a reconciliation queue for the Manager.
- Keep the payment gateway adapter separate. If no live EcoCash/ZIPIT API exists yet, add a clearly marked mock/webhook endpoint so the flow can be tested.

### 7. Administration (Manager only)
- User management: create staff/client users, assign role, activate/deactivate (`is_active`), reset password. Passwords hashed with bcrypt.
- Audit log viewer (read-only, filterable by user, action, entity, date range).

### 8. Alerts (system + all staff view)
- Hourly job (APScheduler or similar) creates `overdue` alerts when `end_date` has passed and `returned_at` is NULL.
- Staff can acknowledge alerts (`acknowledged = true`).

## Filtering, searching and sorting

Implement **server-side** filtering via query parameters (with pagination: `page`, `page_size`, default 20) and a reusable React filter bar component. Use parameterised queries only (SQLAlchemy), never string-built SQL. Debounce the search input (300 ms).

| List | Filters |
|---|---|
| Equipment | search (name/asset_tag), category, status, price range, "available between [start] and [end]" |
| Bookings | search (BK number/client name), status, client, date range (start/end), equipment, created_by |
| Clients | search (name/phone/email), client_type |
| Inspections | booking, equipment, inspection_type, rating, inspector, date range |
| Disputes | status (open/resolved), equipment, client, date range |
| Invoices / Payments | invoice status, payment match_status, provider, currency, date range, client |
| Alerts | type, acknowledged yes/no |
| Audit log | user, action, entity, date range |
| Reports | date range, category, client (overdue, fleet utilisation, payment reconciliation) |

All lists: sortable columns, clear-filters button, filters preserved in the URL query string. Role scoping is applied **before** user filters (e.g. a client can never filter their way into another client's records).

## Validation (apply in the browser with inline messages AND on the server with Pydantic)

- Email: valid format, unique. "Enter a valid email address"
- Password: min 8 chars, a letter and a number
- Start date: not in the past. End date: on or after start date
- Phone: Zimbabwean mobile format, digits only
- Amounts and rates: numeric, greater than 0, 2 decimals
- Asset tag: required, unique, letters/digits/hyphen only. "This asset tag is already in use"
- Photo: JPEG/PNG, max 5 MB, at least one per inspection
- Transaction reference: required for manual payments, not already recorded

## Cross-cutting requirements

- Every create/update/resolve/match action writes an `audit_log` row (user, action, entity, entity_id, timestamp). The audit log is not editable through the app.
- Return plain-language error messages (400/401/403/404/409/422), log technical detail server-side only.
- Use a single `require_roles()` dependency and a single `<RoleGate roles={[...]}>` React component. Do not scatter role checks.
- Keep the menu in sync with the role table above.
- Responsive UI that works on phones.
- Add Alembic migrations for any schema change and seed data (one user per role, 3 categories, ~15 equipment items, a few clients and bookings) so every role can be tested.

## Deliverables

1. The audit table from Step 0.
2. Backend: new/updated routers, schemas, services, RBAC, migrations, seed script.
3. Frontend: forms, filter bar, role-gated menu, pages for each module.
4. Pytest tests: for each role, assert allowed vs forbidden on each endpoint (expect 403 where forbidden), double-booking is rejected, filters return correct results, client cannot see another client's data.
5. A short `CHANGELOG.md` and a test checklist of manual steps per role.

Work module by module (Equipment, Clients, Bookings, Inspections, Disputes, Payments, Admin, Alerts), run the tests after each, and summarise what changed before moving on.
