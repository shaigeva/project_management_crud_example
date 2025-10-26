# Activity Logs & Audit Trails: Detailed Specification

**Status**: 🟡 1/7 requirements implemented (14%)
**Parent**: [Main Spec](../main_spec.md#feature-activity-logs--audit-trails)
**Last Updated**: 2025-01-26

## Rationale

Activity logs provide transparency and compliance by tracking all changes to system entities. Users need to:
- See what changed on tickets, projects, and users
- Know who made changes and when
- Filter historical changes by various criteria
- Maintain an immutable audit trail for compliance

This spec defines the **externally observable behavior** of activity logging, focusing on what users can verify through the API.

---

## REQ-ACTIVITY-001: Log all ticket changes
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a ticket is created, updated, deleted, status changed, assigned, or moved between projects

### Observable Behavior
Every ticket change creates an activity log entry that users can retrieve and verify through the API.

### Acceptance Criteria
- Creating a ticket generates activity log with action="ticket_created"
- Updating ticket fields generates activity log with action="ticket_updated"
  - Log includes which fields changed (old_value, new_value)
- Changing ticket status generates activity log with action="ticket_status_changed"
- Assigning ticket generates activity log with action="ticket_assigned"
- Moving ticket to different project generates activity log with action="ticket_moved"
- Deleting ticket generates activity log with action="ticket_deleted"
- Each log entry includes:
  - `id`: Unique log entry ID
  - `entity_type`: "ticket"
  - `entity_id`: The ticket ID
  - `action`: Action type (ticket_created, ticket_updated, etc.)
  - `actor_id`: User who performed the action
  - `organization_id`: Organization the ticket belongs to
  - `timestamp`: When the action occurred (ISO format)
  - `changes`: Object describing what changed (field_name, old_value, new_value)
  - `metadata`: Additional context (nullable)
- GET /activity_logs?entity_type=ticket&entity_id={id} returns all logs for that ticket
- Logs appear in chronological order (oldest first by default)

### Edge Cases
- Multiple fields updated simultaneously (all changes in one log entry)
- Rapid successive changes (each gets separate log entry)
- Changes by Super Admin vs regular users (both logged)
- Automated system changes (actor_id may be system user)

---

## REQ-ACTIVITY-002: Log project changes
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a project is created, updated, archived, unarchived, or deleted

### Observable Behavior
Every project change creates an activity log entry that users can retrieve and verify through the API.

### Acceptance Criteria
- Creating project generates activity log with action="project_created"
- Updating project details generates activity log with action="project_updated"
- Archiving project generates activity log with action="project_archived"
- Unarchiving project generates activity log with action="project_unarchived"
- Deleting project generates activity log with action="project_deleted"
- Each log entry follows same structure as ticket logs (entity_type="project")
- GET /activity_logs?entity_type=project&entity_id={id} returns all logs for that project
- Logs are organization-scoped (users only see logs for projects in their org)

### Edge Cases
- Project deletion (log remains even after project is deleted)
- Archived project changes (still logged)
- Changes to projects in different organizations

---

## REQ-ACTIVITY-003: Log user actions
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user is created, updated, role changed, activated, deactivated, or deleted

### Observable Behavior
User management actions create activity log entries visible to authorized users.

### Acceptance Criteria
- Creating user generates activity log with action="user_created"
- Updating user generates activity log with action="user_updated"
- Changing user role generates activity log with action="user_role_changed"
- Activating user generates activity log with action="user_activated"
- Deactivating user generates activity log with action="user_deactivated"
- Deleting user generates activity log with action="user_deleted"
- Password changes generate activity log with action="user_password_changed"
  - Does NOT include old or new password values (security)
  - Changes object shows: {"field": "password", "old_value": "[REDACTED]", "new_value": "[REDACTED]"}
- Each log entry follows same structure (entity_type="user")
- GET /activity_logs?entity_type=user&entity_id={id} returns all logs for that user
- Only users with permission to view the user can see their activity logs

### Edge Cases
- Sensitive data (passwords redacted in logs)
- User deletion (log remains after user deleted)
- Super Admin actions vs Org Admin actions (both logged)
- User accessing their own activity logs

---

## REQ-ACTIVITY-004: Retrieve activity log for entity
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests activity logs for a specific entity

### Observable Behavior
Users can retrieve activity logs through the API filtered by entity type and ID.

### Acceptance Criteria
- GET /activity_logs?entity_type={type}&entity_id={id} returns 200 with array of log entries
- If no logs exist, returns empty array []
- Each entry in array has complete log structure
- Logs ordered by timestamp (oldest first by default)
- Query parameter `order=desc` reverses order (newest first)
- Requesting logs for non-existent entity returns empty array (not 404)
- Requesting logs for entity user cannot access returns 403
- Users can only see logs for entities they have permission to view

### Edge Cases
- Entity with no activity logs (returns [])
- Entity that was deleted (logs still accessible if user had permission)
- Long history (many log entries)
- Logs from deleted users (actor_id may reference deleted user)

---

## REQ-ACTIVITY-005: Filter activity logs by date, user, action type
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests activity logs with filtering criteria

### Observable Behavior
Users can filter activity logs using query parameters for date ranges, specific users, and action types.

### Acceptance Criteria
- GET /activity_logs supports query parameters:
  - `entity_type`: Filter by entity type (ticket, project, user, etc.)
  - `entity_id`: Filter by specific entity ID
  - `actor_id`: Filter by user who performed action
  - `action`: Filter by action type (ticket_created, project_updated, etc.)
  - `from_date`: Filter logs after this timestamp (ISO format)
  - `to_date`: Filter logs before this timestamp (ISO format)
  - `organization_id`: Filter by organization (Super Admin only)
- Multiple filters can be combined (AND logic)
- Invalid filter values return 400 with error details
- Empty results return empty array []
- Date filters are inclusive (includes logs at exact timestamps)
- Without entity filters, returns logs for all entities user has access to
- Results are always organization-scoped (unless Super Admin)

### Edge Cases
- Date range with no matching logs
- Invalid date format (returns 400)
- Filtering by deleted actor (returns logs from that user)
- Combining multiple filters
- Large result sets (may need pagination in future)

---

## REQ-ACTIVITY-006: Activity logs respect user permissions
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When users with different roles access activity logs

### Observable Behavior
Users only see activity logs for entities they have permission to view, based on their role and organization.

### Acceptance Criteria
- Users only see logs for entities in their organization
- Read Access users can see logs for tickets/projects they can view
- Write Access users can see logs for tickets/projects they can view
- Project Managers can see all logs in their organization
- Org Admin can see all logs in their organization
- Super Admin can see logs across all organizations
- Attempting to access logs for unauthorized entity returns 403
- When listing logs without entity filter:
  - Returns only logs for entities user can access
  - Applies same permission rules as entity access
- Activity logs themselves cannot be filtered by role (either user has access to entity or doesn't)

### Edge Cases
- User loses access to entity (can no longer see logs)
- User switches organizations (sees different logs)
- Super Admin viewing cross-organization logs
- Logs for entities user previously had access to

---

## REQ-ACTIVITY-007: Activity logs are immutable
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When attempting to modify or delete activity logs

### Observable Behavior
Activity logs cannot be modified or deleted through the API, ensuring audit trail integrity.

### Acceptance Criteria
- No PUT /activity_logs/{id} endpoint exists
- No DELETE /activity_logs/{id} endpoint exists
- No PATCH /activity_logs/{id} endpoint exists
- Attempting PUT/DELETE/PATCH returns 405 Method Not Allowed
- Activity logs are write-once, read-many
- Even Super Admin cannot modify or delete logs
- Log entries created with timestamp are permanent
- System may have internal retention policies (future) but no user-facing deletion

### Edge Cases
- Requests to modify logs (all return 405)
- Requests to delete logs (all return 405)
- Attempting to modify log via other means (not possible)
- Database-level constraints ensure immutability

---

## Implementation Notes

### Activity Log Structure

```json
{
  "id": "log_abc123",
  "entity_type": "ticket",
  "entity_id": "ticket_xyz789",
  "action": "ticket_status_changed",
  "actor_id": "user_123",
  "organization_id": "org_456",
  "timestamp": "2025-01-26T10:30:00Z",
  "changes": {
    "status": {
      "old_value": "TODO",
      "new_value": "IN_PROGRESS"
    }
  },
  "metadata": null
}
```

### Action Types

**Tickets:**
- `ticket_created`
- `ticket_updated`
- `ticket_status_changed`
- `ticket_assigned`
- `ticket_moved`
- `ticket_deleted`

**Projects:**
- `project_created`
- `project_updated`
- `project_archived`
- `project_unarchived`
- `project_deleted`

**Users:**
- `user_created`
- `user_updated`
- `user_role_changed`
- `user_activated`
- `user_deactivated`
- `user_password_changed`
- `user_deleted`

### Changes Object Format

**Single field change:**
```json
{
  "field_name": {
    "old_value": "previous value",
    "new_value": "new value"
  }
}
```

**Multiple field changes:**
```json
{
  "title": {
    "old_value": "Old Title",
    "new_value": "New Title"
  },
  "description": {
    "old_value": "Old description",
    "new_value": "New description"
  }
}
```

**Creation (no old values):**
```json
{
  "created": {
    "title": "New Ticket",
    "status": "TODO",
    "project_id": "proj_123"
  }
}
```

### Future Enhancements (Not in V1)

- Pagination for large result sets
- Export logs to CSV/JSON
- Real-time log streaming (webhooks)
- Advanced filtering (regex, full-text search)
- Log retention policies
- Bulk log retrieval for compliance reports
