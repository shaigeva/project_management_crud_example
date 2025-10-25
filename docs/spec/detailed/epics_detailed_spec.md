# Epics: Detailed Specification

**Status**: 🔴 0/10 requirements implemented (0%)
**Parent**: [Main Spec](../main_spec.md#feature-epics)
**Last Updated**: 2025-01-26

## Rationale

Epics provide a way to group related tickets that span multiple projects within an organization. Users need to:
- Create epics to represent larger initiatives or features
- Add tickets from different projects to an epic
- Track progress across multiple projects
- View all tickets in an epic regardless of which project they belong to
- Organize work at a higher level than individual projects

This spec defines the **externally observable behavior** of epic management, focusing on what users can verify through the API.

---

## REQ-EPIC-001: Create epic within organization
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user creates an epic with required data (name) and optional description within their organization

### Observable Behavior
User can create an epic via API and subsequently verify its existence and correct data through API calls.

### Acceptance Criteria
- POST /epics with valid data returns 201 response
- Response contains created epic with all fields:
  - `id`: Unique identifier (non-empty string)
  - `name`: The provided epic name
  - `description`: The provided description (or null if not provided)
  - `organization_id`: Organization this epic belongs to
  - `created_at`: Timestamp of creation
  - `updated_at`: Timestamp of last update
- After creation, GET /epics/{id} returns the same epic
- Returned data from GET matches what was submitted
- After creation, GET /epics includes the new epic in the list
- Description field is optional (can be omitted)
- Epic is automatically scoped to user's organization

### Edge Cases
- Maximum length name (255 characters)
- Minimum length name (1 character)
- Special characters in name: `!@#$%^&*()`
- Unicode characters: "Epic Español 日本"
- Multiple epics with identical names (all succeed)
- Name-only epic (no description field)

---

## REQ-EPIC-002: Retrieve epic by ID
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific epic by ID

### Observable Behavior
User can retrieve a specific epic by its ID or receive appropriate error if not found or unauthorized.

### Acceptance Criteria
- GET /epics/{id} for existing epic returns 200 with epic data
- Returned data matches what was stored during creation
- GET /epics/{id} for non-existent ID returns 404
- GET /epics/{id} for epic in different organization returns 403
- 404 response includes error message/detail field
- Multiple GET requests for same ID return consistent data

### Edge Cases
- Non-existent epic IDs
- Cross-organization access attempts
- Super Admin can access epics from any organization

---

## REQ-EPIC-003: List epics in organization
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests the list of all epics in their organization

### Observable Behavior
User can retrieve a list of all epics accessible to them through the API.

### Acceptance Criteria
- GET /epics returns 200 with array of epics in user's organization
- If no epics exist, returns empty array []
- Each epic in list has same structure as individual GET response
- All created epics appear in the list
- Deleted epics do not appear in the list
- Users only see epics from their organization
- Super Admin sees epics from all organizations
- Order is consistent across requests

### Edge Cases
- Empty organization (no epics)
- Large number of epics
- After creating/deleting epics
- Cross-organization isolation

---

## REQ-EPIC-004: Update epic details
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user updates an epic's name or description

### Observable Behavior
User can update epic fields and verify the changes through subsequent API calls.

### Acceptance Criteria
- PUT /epics/{id} with update data returns 200 with updated epic
- Updated fields reflect changes
- Non-updated fields remain unchanged
- updated_at timestamp changes
- After update, GET /epics/{id} returns updated data
- Partial updates supported (can update just name or just description)
- Empty update (no fields) succeeds with no changes
- Returns 404 if epic doesn't exist
- Returns 403 if user doesn't have permission or epic in different organization

### Edge Cases
- Update name only
- Update description only
- Update both fields
- Empty update command
- Set description to null
- Maximum length validations still apply

---

## REQ-EPIC-005: Delete epic
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When an authorized user deletes an epic

### Observable Behavior
Epic is removed from the system and subsequent attempts to access it fail.

### Acceptance Criteria
- DELETE /epics/{id} returns 204 on success
- After deletion, GET /epics/{id} returns 404
- After deletion, epic does not appear in GET /epics list
- Deleting epic does not delete associated tickets (tickets remain in their projects)
- Tickets that were in the epic lose their epic association
- Returns 404 if epic doesn't exist
- Returns 403 if user doesn't have permission or epic in different organization
- Only Admin can delete epics
- Super Admin can delete epics from any organization

### Edge Cases
- Delete epic with many tickets
- Delete epic with no tickets
- Delete non-existent epic
- Cross-organization delete attempts
- Verify tickets still exist after epic deletion

---

## REQ-EPIC-006: Add ticket to epic
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user adds a ticket to an epic

### Observable Behavior
Ticket becomes associated with the epic and appears when listing epic's tickets.

### Acceptance Criteria
- POST /epics/{epic_id}/tickets with ticket_id adds ticket to epic
- Returns 200 with updated epic or ticket association
- After adding, GET /epics/{epic_id}/tickets includes the ticket
- Can add tickets from different projects (within same organization)
- Cannot add ticket from different organization
- Cannot add same ticket twice (idempotent - second add succeeds but no duplicate)
- Returns 404 if epic or ticket doesn't exist
- Returns 403 if epic or ticket in different organization
- Admin and Project Manager can add tickets to epics

### Edge Cases
- Add ticket from different project (same org) - succeeds
- Add ticket from different organization - fails 403
- Add already-added ticket - idempotent (succeeds, no duplicate)
- Add ticket to non-existent epic - fails 404
- Add non-existent ticket - fails 404
- Epic can contain tickets from multiple projects

---

## REQ-EPIC-007: Remove ticket from epic
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user removes a ticket from an epic

### Observable Behavior
Ticket is no longer associated with the epic and doesn't appear when listing epic's tickets.

### Acceptance Criteria
- DELETE /epics/{epic_id}/tickets/{ticket_id} removes ticket from epic
- Returns 204 on success
- After removal, GET /epics/{epic_id}/tickets does not include the ticket
- Removing ticket doesn't delete the ticket (ticket remains in its project)
- Removing non-associated ticket succeeds (idempotent)
- Returns 404 if epic or ticket doesn't exist
- Returns 403 if epic or ticket in different organization
- Admin and Project Manager can remove tickets from epics

### Edge Cases
- Remove ticket not in epic - idempotent (succeeds)
- Remove ticket from non-existent epic - fails 404
- Remove non-existent ticket - fails 404
- Ticket remains in its project after removal

---

## REQ-EPIC-008: List tickets in epic (from multiple projects)
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests all tickets in an epic

### Observable Behavior
User can retrieve all tickets associated with an epic, regardless of which project they belong to.

### Acceptance Criteria
- GET /epics/{epic_id}/tickets returns 200 with array of tickets
- If no tickets in epic, returns empty array []
- Each ticket has full ticket data (not just IDs)
- Tickets from multiple projects are all returned
- All tickets belong to the same organization as the epic
- Order is consistent across requests
- Returns 404 if epic doesn't exist
- Returns 403 if epic in different organization

### Edge Cases
- Empty epic (no tickets)
- Epic with tickets from single project
- Epic with tickets from multiple projects
- Epic with many tickets
- Cross-organization access attempts

---

## REQ-EPIC-009: Epics are organization-scoped
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When users in different organizations work with epics

### Observable Behavior
Epics and their ticket associations are completely isolated by organization. Users can only access epics within their organization.

### Acceptance Criteria
- Epics belong to a specific organization
- Users can only create epics in their organization
- Users can only see epics from their organization in lists
- Users cannot access epics from other organizations (403)
- Super Admin can access epics from all organizations
- Can only add tickets from same organization to an epic
- Attempting to add cross-organization ticket fails with 403
- Epic-ticket relationships respect organization boundaries

### Edge Cases
- User with no organization cannot create epics
- Cross-organization epic access attempts return 403
- Cross-organization ticket association attempts return 403
- Super Admin cross-organization access succeeds

---

## REQ-EPIC-010: Handle validation and not-found errors
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user provides invalid data or references non-existent resources

### Observable Behavior
User receives clear error messages when providing invalid data or referencing missing resources.

### Acceptance Criteria
- POST /epics with invalid data returns 400 or 422 status
- Response includes clear error message explaining what is invalid
- Error message identifies which field has the problem
- No epic is created when validation fails
- Empty name is rejected (required field)
- Name exceeding max length (255 chars) is rejected
- Invalid data types are rejected (e.g., number for name field)
- Operations on non-existent epics return 404
- Operations on epics in different organization return 403
- Adding non-existent ticket to epic returns 404

### Edge Cases
- Missing required field (name)
- Empty string for name
- Name too long (>255 characters)
- Wrong data type for field
- Non-existent epic ID
- Non-existent ticket ID
- Cross-organization access attempts
