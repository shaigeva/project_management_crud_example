# Task Implementation Plan: Add activity logging to ticket operations

**Task Status**: 🔄 In Progress
**Date**: 2025-01-26
**Implements Requirements**: REQ-ACTIVITY-001

## Behaviors to Implement

### From REQ-ACTIVITY-001: Log all ticket changes

**Observable Behavior**:
- When tickets are created, updated, deleted, status changed, assigned, or moved
- Activity log entries are created capturing the change
- Logs include: actor (who), entity (what), action (type), changes (details), timestamp (when)

**Acceptance Criteria** (from spec):
- Creating ticket generates log with action="ticket_created"
- Updating ticket fields generates log with action="ticket_updated" (includes old/new values)
- Changing status generates log with action="ticket_status_changed"
- Assigning ticket generates log with action="ticket_assigned"
- Moving ticket generates log with action="ticket_moved"
- Deleting ticket generates log with action="ticket_deleted"

## Implementation Plan

### Ticket API Changes

**File**: `project_management_crud_example/routers/ticket_api.py`

For each endpoint, after successful operation:
1. Get ticket organization_id (from project)
2. Create ActivityLogCreateCommand with appropriate action
3. Call `repo.activity_logs.create(command)`

**Endpoints to instrument:**

- [ ] POST /api/tickets - ticket_created
  - After ticket creation, log with changes={"created": {full ticket data}}

- [ ] PUT /api/tickets/{id} - ticket_updated
  - Before update, get old ticket
  - After update, log with changes={field: {old_value, new_value}} for each changed field

- [ ] PUT /api/tickets/{id}/status - ticket_status_changed
  - Before status change, get old status
  - After change, log with changes={"status": {old_value, new_value}}

- [ ] PUT /api/tickets/{id}/assignee - ticket_assigned
  - Before assignment, get old assignee
  - After change, log with changes={"assignee_id": {old_value, new_value}}

- [ ] PUT /api/tickets/{id}/project - ticket_moved
  - Before move, get old project_id
  - After move, log with changes={"project_id": {old_value, new_value}}

- [ ] DELETE /api/tickets/{id} - ticket_deleted
  - Before deletion, capture ticket snapshot
  - After deletion, log with changes={"deleted": {ticket snapshot}}

### Helper Function

Create helper function in ticket_api.py:

```python
def _log_ticket_activity(
    repo: Repository,
    ticket: Ticket,
    action: ActionType,
    actor_id: str,
    changes: dict,
) -> None:
    """Create activity log entry for ticket operation."""
    # Get organization from project
    project = repo.projects.get_by_id(ticket.project_id)
    if not project:
        return  # Shouldn't happen, but defensive

    command = ActivityLogCreateCommand(
        entity_type="ticket",
        entity_id=ticket.id,
        action=action,
        actor_id=actor_id,
        organization_id=project.organization_id,
        changes=changes,
    )
    repo.activity_logs.create(command)
```

### Imports to Add

Need to import:
```python
from project_management_crud_example.domain_models import (
    ActionType,
    ActivityLogCreateCommand,
    # ... existing imports
)
```

## Test Planning

### API Tests

**File**: `tests/api/test_ticket_api.py`

**New test class: TestTicketActivityLogging**

Tests verify that activity logs are created:

1. `test_create_ticket_creates_activity_log`
   - Create ticket
   - Query activity logs for that ticket
   - Verify log exists with action=ticket_created
   - Verify changes contains created data

2. `test_update_ticket_creates_activity_log`
   - Create ticket
   - Update ticket fields (title, description)
   - Query activity logs
   - Verify log with action=ticket_updated
   - Verify changes contains old/new values for updated fields

3. `test_change_ticket_status_creates_activity_log`
   - Create ticket (status=TODO)
   - Change status to IN_PROGRESS
   - Query logs
   - Verify log with action=ticket_status_changed
   - Verify changes shows status transition

4. `test_assign_ticket_creates_activity_log`
   - Create ticket (no assignee)
   - Assign to user
   - Query logs
   - Verify log with action=ticket_assigned
   - Verify changes shows assignee change

5. `test_move_ticket_creates_activity_log`
   - Create ticket in project A
   - Move to project B
   - Query logs
   - Verify log with action=ticket_moved
   - Verify changes shows project_id change

6. `test_delete_ticket_creates_activity_log`
   - Create ticket
   - Delete ticket
   - Query logs (ticket deleted, but logs remain)
   - Verify log with action=ticket_deleted
   - Verify changes contains ticket snapshot

7. `test_activity_log_captures_actor`
   - Create ticket as user A
   - Verify log has actor_id = user A's ID

8. `test_multiple_operations_create_multiple_logs`
   - Create ticket
   - Update it
   - Change status
   - Query logs
   - Verify 3 logs exist in chronological order

**Repository tests**: Not needed - repository already tested in Task 1

**Estimated**: 8 new API tests

## Implementation Notes

### Changes Object Structure

**For creation:**
```json
{
  "created": {
    "title": "New Ticket",
    "description": "Description",
    "status": "TODO",
    "priority": "HIGH",
    "project_id": "proj_123",
    "reporter_id": "user_456"
  }
}
```

**For updates:**
```json
{
  "title": {"old_value": "Old", "new_value": "New"},
  "description": {"old_value": "Old desc", "new_value": "New desc"}
}
```

**For status change:**
```json
{
  "status": {"old_value": "TODO", "new_value": "IN_PROGRESS"}
}
```

**For assignment:**
```json
{
  "assignee_id": {"old_value": null, "new_value": "user_789"}
}
```

**For move:**
```json
{
  "project_id": {"old_value": "proj_A", "new_value": "proj_B"}
}
```

**For deletion:**
```json
{
  "deleted": {
    "id": "ticket_123",
    "title": "Deleted Ticket",
    "status": "TODO"
  }
}
```

### Error Handling

- If activity log creation fails, should we fail the operation?
- Decision: Log the error but don't fail the operation
- Activity logging is important but shouldn't break user operations
- Use try-except around log creation

### Testing via API

Since we're instrumenting API endpoints:
- Create operations via API
- Query activity logs via repository (API endpoint comes in Task 5)
- Verify logs were created with correct data

## Checklist

Implementation:
- [ ] Add imports (ActionType, ActivityLogCreateCommand)
- [ ] Create _log_ticket_activity helper function
- [ ] Instrument POST /tickets (create)
- [ ] Instrument PUT /tickets/{id} (update)
- [ ] Instrument PUT /tickets/{id}/status (status change)
- [ ] Instrument PUT /tickets/{id}/assignee (assign)
- [ ] Instrument PUT /tickets/{id}/project (move)
- [ ] Instrument DELETE /tickets/{id} (delete)

Testing:
- [ ] Write 8 API tests for activity logging
- [ ] Run validations until zero errors

Status Updates:
- [ ] Update REQ-ACTIVITY-001 status: 🔴 → ✅
- [ ] Update Task 2 status: 🔄 → ✅
