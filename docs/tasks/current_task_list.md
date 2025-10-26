# Current Task List - Implement Epics Feature

**Created**: 2025-01-26
**Spec Reference**: [Epics](../spec/detailed/epics_detailed_spec.md)

---

## Task 1: Implement Epic CRUD operations (REQ-EPIC-001 through REQ-EPIC-005)
**Status**: ✅ Complete
**Implements**: REQ-EPIC-001, REQ-EPIC-002, REQ-EPIC-003, REQ-EPIC-004, REQ-EPIC-005, REQ-EPIC-009, REQ-EPIC-010

Implement core CRUD operations for epics with organization scoping and role-based permissions.

**What to implement**:
- Domain model: Epic with id, name, description, organization_id, created_at, updated_at
- ORM model: EpicORM with database schema
- Repository: create, get_by_id, get_by_organization_id, get_all, update, delete methods
- API endpoints:
  - POST /api/epics (create)
  - GET /api/epics/{id} (retrieve)
  - GET /api/epics (list with org scoping)
  - PUT /api/epics/{id} (update)
  - DELETE /api/epics/{id} (delete)
- Permission rules:
  - Admin, PM can create/update epics
  - Admin can delete epics
  - All roles can view epics in their organization
  - Super Admin can access all organizations
- Comprehensive tests: API tests and repository tests

**Acceptance criteria**:
- POST /api/epics creates epic in user's organization
- GET /api/epics/{id} retrieves epic or returns 404/403
- GET /api/epics lists only user's organization epics
- PUT /api/epics/{id} updates epic fields
- DELETE /api/epics/{id} removes epic
- Organization scoping enforced
- Validation errors handled (empty name, too long, etc.)

---

## Task 2: Implement epic-ticket relationships (REQ-EPIC-006, REQ-EPIC-007, REQ-EPIC-008)
**Status**: ✅ Complete
**Implements**: REQ-EPIC-006, REQ-EPIC-007, REQ-EPIC-008

Implement many-to-many relationship between epics and tickets.

**What to implement**:
- Database: epic_tickets association table (epic_id, ticket_id)
- ORM model: EpicTicketORM for association table
- Domain model: Update Epic model if needed for ticket relationship
- Repository methods:
  - add_ticket_to_epic(epic_id, ticket_id)
  - remove_ticket_from_epic(epic_id, ticket_id)
  - get_tickets_in_epic(epic_id)
- API endpoints:
  - POST /api/epics/{id}/tickets (add ticket)
  - DELETE /api/epics/{id}/tickets/{ticket_id} (remove ticket)
  - GET /api/epics/{id}/tickets (list tickets)
- Cross-project support: tickets from different projects can be in same epic
- Organization validation: epic and ticket must be in same organization
- Comprehensive tests

**Acceptance criteria**:
- POST /api/epics/{id}/tickets adds ticket to epic
- Can add tickets from different projects (same org)
- Cannot add tickets from different organizations (403)
- Adding same ticket twice is idempotent
- DELETE /api/epics/{id}/tickets/{ticket_id} removes association
- Removing ticket doesn't delete the ticket
- Removal is idempotent
- GET /api/epics/{id}/tickets returns all tickets in epic
- Returns tickets from multiple projects
- Deleting epic removes associations but not tickets

---

## Completion

- [ ] Task 1 marked ✅
- [ ] REQ-EPIC-001 through REQ-EPIC-005 marked ✅ in spec
- [ ] REQ-EPIC-009 marked ✅ in spec
- [ ] REQ-EPIC-010 marked ✅ in spec
- [ ] Task 2 marked ✅
- [ ] REQ-EPIC-006 marked ✅ in spec
- [ ] REQ-EPIC-007 marked ✅ in spec
- [ ] REQ-EPIC-008 marked ✅ in spec
- [ ] Update main_spec.md status to 🟢 10/10 (100%)
- [ ] Archive to `archive/2025-01-26_implement_epics.md`
