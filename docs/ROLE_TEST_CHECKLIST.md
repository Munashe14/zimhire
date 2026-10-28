# Role test checklist

## Manual QA checklist per role

### Clerk
- [ ] Login with `booking_clerk / Clerk123!`
- [ ] Access dashboard and equipment view
- [ ] Create a new client
- [ ] Create a booking request or availability check
- [ ] Confirm the role menu hides manager-only admin sections

### Supervisor
- [ ] Login with `depot_supervisor / Supervisor123!`
- [ ] Access dashboard and equipment administrative tools
- [ ] Create or update equipment records
- [ ] Confirm report access is limited to overdue/report subsets
- [ ] Confirm admin section is hidden

### Manager
- [ ] Login with `ops_manager / Manager123!`
- [ ] Access all menu sections including reports and administration
- [ ] Create equipment and clients
- [ ] Confirm user-management/admin links are visible
- [ ] Validate role gating matches the backend policy

### Client
- [ ] Login with `client_user / Client123!`
- [ ] Access dashboard and own bookings only
- [ ] Confirm hidden sections for equipment, clients, and admin modules
- [ ] Confirm the role portal does not expose manager or clerk-only tools

## Automated checks

- Run `pytest` in `backend` after each role-related change.
- Validate the role alias regression tests in `backend/tests/test_roles.py`.
- Verify login and signup still succeed after database normalization.
