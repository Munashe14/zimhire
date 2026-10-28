# State Transition Rules

## Equipment Status Transitions

### Current Status: Available
- Can transition to: Reserved, Rented Out, Under Maintenance, Unavailable
- Cannot be rented if transitioning to Under Maintenance or Unavailable

### Current Status: Reserved
- Can transition to: Available (if reservation cancelled), Rented Out
- Cannot be rented again until reservation is resolved

### Current Status: Rented Out
- Can transition to: Available (after return inspection), Under Maintenance (if damage detected)
- Cannot be rented until returned and cleared

### Current Status: Under Maintenance
- Can transition to: Available (after maintenance complete), Unavailable
- Cannot be rented until maintenance is complete

### Current Status: Unavailable
- Can transition to: Available
- Cannot be rented until made available

## Booking Status Transitions

### Current Status: Pending
- Can transition to: Confirmed, Cancelled
- Confirmed booking reserves equipment

### Current Status: Confirmed
- Can transition to: Active (on dispatch), Cancelled
- Active booking marks equipment as Rented Out

### Current Status: Active
- Can transition to: Completed (on return), Cancelled (with penalties)
- Completed booking releases equipment back to Available

### Current Status: Completed
- Final state - no further transitions
- Equipment returned and cleared

### Current Status: Cancelled
- Final state - no further transitions
- Equipment released back to Available

## Invoice Status Transitions

### Current Status: Draft
- Can transition to: Issued, Cancelled
- Issued invoice is sent to client

### Current Status: Issued
- Can transition to: Partially Paid, Paid, Overdue, Cancelled
- Overdue if past due date without payment

### Current Status: Partially Paid
- Can transition to: Paid, Overdue
- Paid when full amount received

### Current Status: Paid
- Final state - no further transitions
- Fully settled

### Current Status: Overdue
- Can transition to: Partially Paid, Paid
- Paid when full amount received

### Current Status: Cancelled
- Final state - no further transitions
- Invoice voided

## Payment Status Transitions

### Current Status: Pending
- Can transition to: Matched, Partially Matched, Failed, Unmatched
- Pending payment awaiting processing

### Current Status: Matched
- Final state - no further transitions
- Payment successfully matched to invoice

### Current Status: Partially Matched
- Can transition to: Matched
- Remaining payment received

### Current Status: Failed
- Final state - no further transitions
- Payment processing failed

### Current Status: Unmatched
- Can transition to: Matched, Partially Matched
- Manually matched to invoice

## Damage Dispute Status Transitions

### Current Status: Open
- Can transition to: Under Review, Closed
- Under Review when assigned to reviewer

### Current Status: Under Review
- Can transition to: Resolved, Closed
- Resolved when decision made

### Current Status: Resolved
- Final state - no further transitions
- Dispute resolved with documented decision

### Current Status: Closed
- Final state - no further transitions
- Dispute closed without resolution

## Alert Status Transitions

### Current Status: Open
- Can transition to: Acknowledged, Resolved
- Acknowledged when staff acknowledges alert

### Current Status: Acknowledged
- Can transition to: Resolved
- Resolved when issue is fixed

### Current Status: Resolved
- Final state - no further transitions
- Alert resolved
