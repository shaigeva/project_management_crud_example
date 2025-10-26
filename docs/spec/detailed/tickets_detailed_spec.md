# Tickets: Detailed Specification

**Status**: 🟡 15/17 requirements implemented (88%)
**Parent**: [Main Spec](../main_spec.md#feature-tickets)
**Last Updated**: 2025-01-25

## Rationale

Tickets are the core work items in the project management system. Users need to:
- Create tickets to track tasks, bugs, features
- Assign tickets to team members
- Update ticket status as work progresses
- Move tickets between projects
- View and filter tickets by various criteria

This spec defines the **externally observable behavior** of ticket management, focusing on what users can verify through the API.

---

## REQ-TICKET-001: Create ticket in project
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user creates a ticket with required data (title, project_id) and optional fields

### Observable Behavior
User can create a ticket via API and subsequently verify its existence and correct data through API calls.

### Acceptance Criteria
- POST /tickets with valid data returns 201 response
- Response contains created ticket with all fields:
  - `id`: Unique identifier (non-empty string)
  - `title`: The provided ticket title
  - `description`: The provided description (or null if not provided)
  - `status`: Default status "TODO"
  - `priority`: The provided priority or null
  - `assignee_id`: The provided assignee user ID or null
  - `reporter_id`: ID of user who created the ticket
  - `project_id`: The project this ticket belongs to
  - `created_at`: Timestamp of creation
  - `updated_at`: Timestamp of last update
- After creation, GET /tickets/{id} returns the same ticket
- Returned data from GET matches what was submitted
- After creation, GET /tickets includes the new ticket in the list
- Description, priority, and assignee_id are optional
- Status defaults to "TODO" if not specified
- Reporter is automatically set to current user

### Edge Cases
- Maximum length title (500 characters)
- Minimum length title (1 character)
- Special characters in title
- Unicode characters in title
- Creating ticket without description succeeds
- Creating ticket in non-existent project fails
- Creating ticket in project from different organization fails

---

## REQ-TICKET-002: Retrieve ticket by ID
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific ticket by ID

### Observable Behavior
User can retrieve a specific ticket by its ID or receive appropriate error if not found or unauthorized.

### Acceptance Criteria
- GET /tickets/{id} for existing ticket returns 200 with ticket data
- Returned data matches what was stored during creation
- GET /tickets/{id} for non-existent ID returns 404
- GET /tickets/{id} for ticket in different organization returns 403
- 404 response includes error message/detail field
- Multiple GET requests for same ID return consistent data

### Edge Cases
- Non-existent ticket IDs
- Tickets from different organizations
- Deleted tickets

---

## REQ-TICKET-003: List tickets with filtering
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests the list of tickets, optionally filtered

### Observable Behavior
User can retrieve a list of tickets through the API, with optional filtering by project, status, assignee.

### Acceptance Criteria
- GET /tickets returns 200 with array of all accessible tickets
- If no tickets exist, returns empty array []
- Each ticket in list has same structure as individual GET response
- All created tickets (in user's org) appear in the list
- Deleted tickets do not appear in the list
- Query parameter `project_id` filters to specific project
- Query parameter `status` filters by status
- Query parameter `assignee_id` filters by assignee
- Query parameters can be combined
- Users only see tickets from projects in their organization

### Edge Cases
- Empty database (no tickets)
- Large number of tickets
- Multiple filters combined
- Invalid filter values

---

## REQ-TICKET-004: Update ticket fields
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user updates a ticket's fields (title, description, priority, etc.)

### Observable Behavior
User can update ticket fields via API, with changes persisted and verifiable.

### Acceptance Criteria
- PUT /tickets/{id} with update data returns 200 with updated ticket
- Can update title, description, priority independently
- Can update multiple fields simultaneously
- Cannot update id, created_at, or reporter_id
- Updated ticket has new updated_at timestamp
- Subsequent GET shows updated values
- Updating non-existent ticket returns 404
- Updating ticket in different org returns 403
- Empty/invalid data returns 422 validation error

### Edge Cases
- Partial updates (only one field)
- Updating to empty description (clearing field)
- Validation failures on update

---

## REQ-TICKET-005: Change ticket status
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user changes a ticket's status through the workflow

### Observable Behavior
User can change ticket status following valid workflow transitions.

### Acceptance Criteria
- PUT /tickets/{id}/status with new status returns 200
- Response contains updated ticket with new status
- Valid statuses: "TODO", "IN_PROGRESS", "DONE"
- Status transitions are validated (all transitions allowed in V1)
- Invalid status values return 422 error
- Status change updates updated_at timestamp

### Edge Cases
- Invalid status value
- Same status (no-op, but succeeds)

---

## REQ-TICKET-006: Move ticket to different project
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user moves a ticket from one project to another

### Observable Behavior
User can move tickets between projects within the same organization.

### Acceptance Criteria
- PUT /tickets/{id}/project with new project_id returns 200
- Response contains updated ticket with new project_id
- Can only move to project in same organization
- Moving to non-existent project returns 404
- Moving to project in different org returns 403
- After move, ticket appears in new project's ticket list

### Edge Cases
- Moving to non-existent project
- Moving to project in different organization
- Moving to same project (no-op)

---

## REQ-TICKET-007: Assign ticket to user
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user assigns a ticket to a team member

### Observable Behavior
User can assign/unassign tickets to users in the same organization.

### Acceptance Criteria
- PUT /tickets/{id}/assignee with user_id returns 200
- Response contains ticket with assignee_id set
- Can assign to any active user in same organization
- Can unassign by setting assignee_id to null
- Assigning to non-existent user returns 404
- Assigning to user in different org returns 403
- Assigning to inactive user fails

### Edge Cases
- Assigning to non-existent user
- Assigning to user in different organization
- Unassigning ticket (set to null)

---

## REQ-TICKET-008: Delete ticket
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user deletes a ticket

### Observable Behavior
User can delete tickets with appropriate permissions.

### Acceptance Criteria
- DELETE /tickets/{id} returns 204 (no content)
- After deletion, GET /tickets/{id} returns 404
- Deleted ticket does not appear in list
- Deleting non-existent ticket returns 404
- Only Admin can delete tickets
- Deleting ticket in different org returns 403

### Edge Cases
- Deleting non-existent ticket
- Deleting ticket from different organization
- Permission checks (non-Admin cannot delete)

---

## REQ-TICKET-009: Ticket has predefined fields
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When working with tickets, all required fields are present and validated

### Observable Behavior
Tickets always have consistent structure with predefined fields.

### Acceptance Criteria
- Every ticket has: id, title, description (nullable), status, priority (nullable), assignee_id (nullable), reporter_id, project_id, created_at, updated_at
- Title is required (non-empty string, max 500 chars)
- Description is optional (max 2000 chars)
- Status is enum: TODO, IN_PROGRESS, DONE
- Priority is optional enum: LOW, MEDIUM, HIGH, CRITICAL
- Assignee_id and reporter_id reference users
- Project_id references a project
- Timestamps are ISO format with timezone

### Edge Cases
- Maximum field lengths
- Null vs empty string handling
- Invalid enum values

---

## REQ-TICKET-010: Filter tickets by criteria
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When listing tickets with filter criteria

### Observable Behavior
Users can filter tickets using query parameters.

### Acceptance Criteria
- GET /tickets?project_id={id} returns only tickets from that project
- GET /tickets?status={status} returns only tickets with that status
- GET /tickets?assignee_id={id} returns only tickets assigned to that user
- Filters can be combined (AND logic)
- Invalid filter values ignored or return 400
- Empty results return empty array []

### Edge Cases
- Multiple filters combined
- Non-existent filter values
- Filter with no matching results

---

## REQ-TICKET-011: Tickets are organization-scoped
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When accessing tickets across organizations

### Observable Behavior
Users can only access tickets from projects in their organization.

### Acceptance Criteria
- Users cannot see tickets from other organizations
- Super Admin can see all tickets
- Attempting to access ticket from different org returns 403
- List operations only return tickets from user's organization
- Creating ticket in project from different org fails

### Edge Cases
- Cross-organization access attempts
- Super Admin access to all orgs

---

## REQ-TICKET-012: Handle not-found errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When requesting non-existent tickets

### Observable Behavior
Clear error messages for missing resources.

### Acceptance Criteria
- GET /tickets/{non-existent-id} returns 404
- 404 response includes detail: "Ticket not found"
- Updating non-existent ticket returns 404
- Deleting non-existent ticket returns 404

---

## REQ-TICKET-013: Handle validation errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When providing invalid ticket data

### Observable Behavior
Clear validation error messages.

### Acceptance Criteria
- POST /tickets with invalid data returns 422
- Error message identifies which field is invalid
- Empty title returns validation error
- Title too long (>500 chars) returns validation error
- Invalid status value returns validation error
- Invalid priority value returns validation error

### Edge Cases
- Missing required fields
- Field too long
- Invalid enum values
- Invalid data types

---

## REQ-TICKET-014: Ticket status workflow validation (basic)
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When changing ticket status (V1: hardcoded workflow)

### Observable Behavior
Status changes follow valid workflow rules.

### Acceptance Criteria
- V1: All transitions allowed (TODO ↔ IN_PROGRESS ↔ DONE)
- Invalid status values return 422
- Status is case-sensitive (must match enum exactly)
- See REQ-TICKET-016 for custom workflow validation

### Edge Cases
- Invalid status values
- Hardcoded enum validation (V1)

---

## REQ-TICKET-015: Activity log for ticket changes
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When tickets are modified

### Observable Behavior
Changes to tickets are logged for audit trail.

### Acceptance Criteria
- All ticket operations create activity log entries
- Logged operations: create, update, status change, assign, move, delete
- Activity logs include: entity_id, entity_type, action_type, actor_id, organization_id, timestamp
- Activity logs are queryable via activity log API
- Logs respect organization scoping

### Edge Cases
- All mutation operations logged
- Logs are immutable
- Permission-based log access

---

## REQ-TICKET-016: Validate status against project workflow
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When creating or updating a ticket's status, the status must be valid for the project's workflow

### Observable Behavior
Ticket status values are validated against the project's workflow statuses.

### Acceptance Criteria
**Ticket Creation**:
- POST /api/tickets validates status against project's workflow
- If status provided is not in project's workflow statuses, returns 422
- If status not provided, defaults to first status in workflow (backward compat: "TODO")
- Error message indicates which statuses are valid for the project's workflow
- Project's workflow is determined by project.workflow_id (or org's default workflow)

**Status Update**:
- PUT /api/tickets/{id}/status validates new status against project's workflow
- If new status not in project's workflow statuses, returns 422
- Error message lists valid statuses for the project
- Valid status update succeeds and returns updated ticket

**Ticket Update**:
- PUT /api/tickets/{id} with TicketUpdateCommand does not change status
- Status changes must use dedicated status update endpoint
- General ticket update (title, description, priority) ignores status field

**Status Retrieval**:
- GET /api/tickets/{id} returns ticket with status string
- Status is one of the project's workflow's statuses
- All existing tickets have valid statuses for their project's workflow

### Edge Cases
- Creating ticket with status not in workflow (validation error)
- Creating ticket without status (uses first workflow status)
- Updating to invalid status (validation error)
- Project with custom workflow
- Project with default workflow
- Error messages include valid statuses

---

## REQ-TICKET-017: Validate workflow when moving tickets between projects
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When moving a ticket from one project to another, if projects have different workflows, validate ticket's status

### Observable Behavior
Moving tickets between projects validates status compatibility with target project's workflow.

### Acceptance Criteria
**Moving Ticket**:
- PUT /api/tickets/{id}/project moves ticket to different project
- Before moving, validates ticket's current status is valid in target project's workflow
- If ticket status invalid in target workflow:
  - Returns 400 with error message
  - Error indicates status incompatibility
  - Error lists valid statuses in target workflow
  - Suggests updating status first
- If ticket status valid in target workflow:
  - Move succeeds
  - Returns updated ticket with new project_id
- Same workflow (or both using default): always succeeds

**Status Validation Logic**:
- Get target project's workflow (via workflow_id or default)
- Check if ticket's current status is in target workflow's statuses
- Case-sensitive string match

### Edge Cases
- Moving between projects with same workflow (always succeeds)
- Moving between projects with different workflows (validates status)
- Moving to project where status is invalid (fails with clear error)
- Moving ticket with "TODO" status (usually succeeds - in most workflows)
- Moving ticket with custom status to project with default workflow (likely fails)
