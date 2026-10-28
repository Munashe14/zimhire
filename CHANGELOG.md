# Changelog

## 2026-10-28

### Added
- Role-aware frontend navigation and access gating for the main portal views.
- Equipment and client data-entry panels for staff roles.
- Audit summary and permission matrix documentation for the ZimHire RBAC model.
- Regression coverage around legacy role aliases and canonical user-role handling.

### Fixed
- Resolved the legacy `ADMIN`/`BOOKING_CLERK` enum mismatch that caused login and signup to fail when SQLite rows still contained older role values.
- Normalized stale user-role values in the active local SQLite database to canonical enum members.

### Notes
- The backend already contained most CRUD and service layer logic for equipment, clients, bookings, payments, and reports; the remaining gaps were primarily role-scoping and UI integration.
- The portal now exposes role-specific menu sections and staff entry forms without rewriting the existing API services.
