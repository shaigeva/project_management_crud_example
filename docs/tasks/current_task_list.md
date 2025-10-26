# Current Task List - Custom Workflows

**Created**: 2025-01-26
**Spec Reference**: [Custom Workflows](../spec/detailed/workflows_detailed_spec.md), [Projects](../spec/detailed/projects_detailed_spec.md), [Tickets](../spec/detailed/tickets_detailed_spec.md)

---

## Task 1: Workflow data model and repository layer
**Status**: ✅ Complete
**Implements**: Foundation for all workflow requirements

Create Workflow domain model, database schema, and repository CRUD operations.

**Key behaviors:**
- Workflow entity with id, name, description, statuses, organization_id, is_default
- Status validation (format, uniqueness, non-empty)
- Organization scoping
- Default workflow handling

**Requirements covered**: Foundation for REQ-WORKFLOW-001 through REQ-WORKFLOW-010

---

## Task 2: Workflow API endpoints
**Status**: ✅ Complete
**Implements**: REQ-WORKFLOW-001, REQ-WORKFLOW-002, REQ-WORKFLOW-003, REQ-WORKFLOW-004, REQ-WORKFLOW-005, REQ-WORKFLOW-007, REQ-WORKFLOW-008, REQ-WORKFLOW-010
**Dependencies**: Task 1

Create REST API endpoints for workflow management with permissions and validation.

**Endpoints:**
- POST /api/workflows - Create workflow (PM+)
- GET /api/workflows - List workflows (all users)
- GET /api/workflows/{id} - Get workflow (all users)
- PUT /api/workflows/{id} - Update workflow (PM+)
- DELETE /api/workflows/{id} - Delete workflow (Admin+)

**Key behaviors:**
- Role-based permissions (PM+ create/update, Admin+ delete)
- Organization scoping
- Validation (status format, non-empty, no duplicates)
- Cannot delete workflow if projects use it
- Cannot update workflow if it breaks existing tickets (REQ-WORKFLOW-009)

---

## Task 3: Default workflow initialization
**Status**: ⏳ Pending
**Implements**: REQ-WORKFLOW-006
**Dependencies**: Task 1

Ensure each organization has a default workflow.

**Key behaviors:**
- Create default workflow when organization is created
- Default workflow: name="Default Workflow", statuses=["TODO", "IN_PROGRESS", "DONE"], is_default=true
- Cannot delete default workflows
- Migration: create default workflows for existing organizations

---

## Task 4: Project-workflow integration
**Status**: ⏳ Pending
**Implements**: REQ-PROJ-011
**Dependencies**: Task 1, Task 3

Update Project model and API to reference workflows.

**Key behaviors:**
- Add workflow_id field to Project (nullable, defaults to org's default workflow)
- Project creation accepts optional workflow_id
- Project update can change workflow_id (validates ticket compatibility)
- Workflow must be in same organization
- Projects retrieve includes workflow_id

---

## Task 5: Ticket status workflow validation
**Status**: ⏳ Pending
**Implements**: REQ-TICKET-016, REQ-TICKET-017
**Dependencies**: Task 4

Update ticket operations to validate status against project's workflow.

**Key behaviors:**
- Ticket creation validates status against project's workflow
- Status defaults to workflow.statuses[0] if not provided
- Status update validates against project's workflow
- Moving tickets validates status compatibility with target project's workflow
- Error messages include valid statuses for the workflow

**Breaking changes:**
- Ticket status changes from enum to string validation
- Status validation is dynamic (workflow-based) not static (enum-based)

---

## Completion

- [ ] All tasks marked ✅
- [ ] All 10 REQ-WORKFLOW requirements marked ✅ in workflows_detailed_spec.md
- [ ] REQ-PROJ-011 marked ✅ in projects_detailed_spec.md
- [ ] REQ-TICKET-016, REQ-TICKET-017 marked ✅ in tickets_detailed_spec.md
- [ ] Update main_spec.md feature statuses
- [ ] Archive to `archive/2025-01-26_custom_workflows.md`
