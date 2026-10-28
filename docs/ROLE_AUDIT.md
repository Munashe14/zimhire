# ZimHire RBAC and feature audit

## Audit summary

| Module | Existing backend endpoints | Existing UI | Gaps / status |
|---|---|---|---|
| Authentication | `POST /api/auth/login`, `POST /api/auth/signup`, `POST /api/auth/refresh`, `GET /api/auth/users`, `PUT /api/auth/users/{id}` | Login + sign-up form | Role aliases normalized; portal session now stores user role and hides menu items by role |
| Equipment | `POST /api/equipment`, `GET /api/equipment`, `GET /api/equipment/{id}`, `PUT /api/equipment/{id}`, category CRUD | Inventory dashboard table | Staff add/edit panel added to portal; server-side filtering remains API-driven and can be extended |
| Clients | `POST /api/clients`, `GET /api/clients`, `GET /api/clients/{id}`, `PUT /api/clients/{id}` | None | Client creation form added to staff portal |
| Bookings | `POST /api/bookings`, `GET /api/bookings`, `GET /api/bookings/{id}`, `PUT /api/bookings/{id}`, availability checks | None | Booking queue placeholder with backend hooks; availability validation is server-side already |
| Inspections | `POST /api/inspections`, `GET /api/inspections`, `PUT /api/inspections/{id}` | None | Requires role-specific forms and photo upload flow for full deployment |
| Damage disputes | `POST /api/disputes`, `GET /api/disputes`, `PUT /api/disputes/{id}` | None | Backend exists; UI not yet expanded |
| Invoices / payments | `POST /api/invoices`, `GET /api/invoices`, `PUT /api/invoices/{id}`, `POST /api/payments`, `GET /api/payments`, unmatched queue | None | Manager reconciliation flow is available in backend, UI placeholders remain |
| Reports | `GET /api/reports/dashboard`, `GET /api/reports/equipment-utilization`, `GET /api/reports/bookings`, `GET /api/reports/revenue` | None | Dashboard aggregation exists; role-scoped UI still needs deeper reporting pages |
| Administration | `GET /api/auth/users`, audit log endpoints exist in services | None | Manager role gating included in the UI shell |

## Role matrix

| Scope | Clerk | Supervisor | Manager | Client |
|---|---|---|---|---|
| Dashboard | Yes | Yes | Yes | Yes |
| Equipment view | Yes | Yes | Yes | No |
| Equipment create/edit | Limited UI entry form | Yes | Yes | No |
| Clients | Yes | View only in backend | Yes | No |
| Bookings | Create/list own or all depending on backend policy | View only | Full | Own bookings only |
| Reports | No | Overdue-only subset | All | No |
| Admin / audit log | No | No | Yes | No |

## Critical implementation notes

- The backend is already largely complete for CRUD services and RBAC dependencies.
- The stale issue was caused by legacy role names stored in SQLite because older seed data used `ADMIN` and alias roles.
- The canonical values are now mapped to `clerk`, `supervisor`, `manager`, and `client`.
- The front-end now shows a role-scoped menu and forms that match the staff-only operational workflows.
