# Current Task List: Tickets Feature Implementation

**Feature**: Tickets (Work Items)
**Status**: 🔵 Planning
**Started**: 2025-01-25
**Spec**: [docs/spec/detailed/tickets_detailed_spec.md](../spec/detailed/tickets_detailed_spec.md)

---

## Phase 1: Domain & Data Layer

### Task 1.1: Create Ticket domain models
**Requirements**: REQ-TICKET-009 (predefined fields)
- Create `TicketStatus` enum (TODO, IN_PROGRESS, DONE)
- Create `TicketPriority` enum (LOW, MEDIUM, HIGH, CRITICAL)
- Create `TicketData` model (title, description, priority)
- Create `Ticket` model (extends TicketData with id, status, assignee_id, reporter_id, project_id, timestamps)
- Create `TicketCreateCommand` model
- Create `TicketUpdateCommand` model

### Task 1.2: Create Ticket ORM model
**Requirements**: REQ-TICKET-009
- Create `TicketORM` in orm_data_models.py
- Define table structure with all fields
- Add foreign keys to projects and users tables
- Add indexes for common queries (project_id, status, assignee_id)

### Task 1.3: Create Ticket repository layer
**Requirements**: REQ-TICKET-001, REQ-TICKET-002, REQ-TICKET-003, REQ-TICKET-004, REQ-TICKET-008
- Create `Repository.Tickets` nested class
- Implement `create()` - creates ticket with reporter_id from current user
- Implement `get_by_id()` - retrieves single ticket
- Implement `get_all()` - lists all tickets
- Implement `get_by_project_id()` - filters by project
- Implement `get_by_filters()` - filters by status, assignee, project
- Implement `update()` - updates ticket fields
- Implement `update_status()` - changes status
- Implement `update_project()` - moves to different project
- Implement `update_assignee()` - assigns/unassigns
- Implement `delete()` - deletes ticket
- Write comprehensive repository tests

---

## Phase 2: API Layer

### Task 2.1: Create Tickets API router
**Requirements**: All REQ-TICKET-*
- Create `routers/ticket_api.py`
- Set up router with prefix `/api/tickets`

### Task 2.2: Implement POST /tickets endpoint
**Requirements**: REQ-TICKET-001, REQ-TICKET-009, REQ-TICKET-011, REQ-TICKET-013
- Authorization: Admin, PM, Write users can create
- Validate project exists and is in user's organization
- Set reporter_id to current user
- Set default status to TODO
- Return 201 with created ticket
- Write API tests

### Task 2.3: Implement GET /tickets/{id} endpoint
**Requirements**: REQ-TICKET-002, REQ-TICKET-011, REQ-TICKET-012
- Authorization: Users can view tickets from their org's projects
- Super Admin can view any ticket
- Return 404 for non-existent tickets
- Return 403 for cross-org access
- Write API tests

### Task 2.4: Implement GET /tickets endpoint with filtering
**Requirements**: REQ-TICKET-003, REQ-TICKET-010, REQ-TICKET-011
- Authorization: Users see tickets from their org's projects only
- Super Admin sees all tickets
- Support query params: project_id, status, assignee_id
- Return empty array if no tickets
- Write API tests for filtering combinations

### Task 2.5: Implement PUT /tickets/{id} endpoint
**Requirements**: REQ-TICKET-004, REQ-TICKET-011, REQ-TICKET-012, REQ-TICKET-013
- Authorization: Admin, PM, Write users can update
- Can update title, description, priority
- Cannot update id, timestamps, reporter_id
- Return 404 for non-existent tickets
- Return 403 for cross-org access
- Validate field constraints
- Write API tests

### Task 2.6: Implement PUT /tickets/{id}/status endpoint
**Requirements**: REQ-TICKET-005, REQ-TICKET-014
- Authorization: Admin, PM, Write users can change status
- Validate status enum value
- V1: All transitions allowed
- Update updated_at timestamp
- Write API tests

### Task 2.7: Implement PUT /tickets/{id}/project endpoint
**Requirements**: REQ-TICKET-006, REQ-TICKET-011
- Authorization: Admin, PM can move tickets
- Validate target project exists
- Validate target project in same organization
- Return 403 if moving cross-org
- Write API tests

### Task 2.8: Implement PUT /tickets/{id}/assignee endpoint
**Requirements**: REQ-TICKET-007, REQ-TICKET-011
- Authorization: Admin, PM can assign tickets
- Validate assignee user exists and is active
- Validate assignee in same organization
- Allow null to unassign
- Write API tests

### Task 2.9: Implement DELETE /tickets/{id} endpoint
**Requirements**: REQ-TICKET-008, REQ-TICKET-011, REQ-TICKET-012
- Authorization: Admin only can delete
- Return 404 for non-existent tickets
- Return 403 for cross-org access
- Return 204 on success
- Write API tests

### Task 2.10: Register ticket router in app.py
- Import ticket_api router
- Add `app.include_router(ticket_api.router)`

---

## Phase 3: Testing & Documentation

### Task 3.1: Write comprehensive API tests
**Requirements**: All REQ-TICKET-*
- Test all CRUD operations
- Test authorization for each role (Admin, PM, Write, Read, Super Admin)
- Test cross-organization access prevention
- Test filtering combinations
- Test validation errors
- Test complete workflow (create → assign → update status → move → delete)
- Ensure all tests pass with 0 errors

### Task 3.2: Run validations
- Run `./devtools/run_all_agent_validations.sh`
- Fix any lint, format, type, or test errors
- Ensure all 239+ tests pass

### Task 3.3: Update spec statuses
- Mark implemented requirements as ✅ in detailed spec
- Update main spec with completion percentage
- Update "Last Updated" dates

---

## Summary

**Total Tasks**: 16 tasks across 3 phases
**Estimated Complexity**: Large (similar to Projects but more complex)

**Key Implementation Notes**:
- Tickets belong to projects (project_id FK)
- Reporter is auto-set to current user on creation
- Organization scoping enforced via project relationship
- Multiple specialized update endpoints for different operations
- Admin-only deletion, but PM/Write can create/update
- V1: Simple status workflow with all transitions allowed
- Activity logging (REQ-TICKET-015) deferred to future

**Dependencies**:
- Projects feature (already implemented ✅)
- Users feature (partial - creation works via tests)
- Organizations feature (implemented ✅)
