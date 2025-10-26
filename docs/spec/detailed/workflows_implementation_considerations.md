# Custom Workflows: Implementation Considerations

**Date**: 2025-01-26
**Status**: Planning Document

## Overview

This document outlines the technical considerations, migration strategy, and potential issues for implementing custom workflows.

---

## Data Model Changes

### New Entity: Workflow

```
Workflow:
  - id: string (UUID)
  - name: string (max 255 chars)
  - description: string | null (max 1000 chars)
  - statuses: list[string] (non-empty array, e.g., ["TODO", "IN_PROGRESS", "DONE"])
  - organization_id: string (FK to Organization)
  - is_default: boolean (each org has exactly one default workflow)
  - created_at: datetime
  - updated_at: datetime
```

**Constraints:**
- statuses must be non-empty array
- status names must match pattern: `^[A-Z0-9_-]+$`
- no duplicate status names within a workflow
- exactly one is_default=true per organization

### Updated Entity: Project

```diff
Project:
  - id: string
  - name: string
  - description: string | null
  - organization_id: string
  - is_archived: boolean
  - archived_at: datetime | null
+ - workflow_id: string | null (FK to Workflow, null = use org's default)
  - created_at: datetime
  - updated_at: datetime
```

**Constraints:**
- workflow_id must reference workflow in same organization
- if workflow_id is null, project uses org's default workflow

### Updated Entity: Ticket

```diff
Ticket:
  - id: string
  - title: string
  - description: string | null
- - status: TicketStatus (enum: TODO | IN_PROGRESS | DONE)
+ - status: string (must be in project's workflow statuses)
  - priority: TicketPriority | null
  - assignee_id: string | null
  - reporter_id: string
  - project_id: string
  - created_at: datetime
  - updated_at: datetime
```

**Breaking Change:**
- status changes from enum to string
- validation changes from enum check to dynamic workflow check

---

## Migration Strategy

### Phase 1: Schema Migration

1. **Create workflows table**
   ```sql
   CREATE TABLE workflows (
     id TEXT PRIMARY KEY,
     name TEXT NOT NULL,
     description TEXT,
     statuses TEXT NOT NULL,  -- JSON array
     organization_id TEXT NOT NULL,
     is_default BOOLEAN NOT NULL DEFAULT 0,
     created_at TEXT NOT NULL,
     updated_at TEXT NOT NULL,
     FOREIGN KEY (organization_id) REFERENCES organizations(id)
   )
   CREATE UNIQUE INDEX idx_workflows_org_default
     ON workflows(organization_id, is_default)
     WHERE is_default = 1
   ```

2. **Add workflow_id to projects table**
   ```sql
   ALTER TABLE projects ADD COLUMN workflow_id TEXT
   -- No FK constraint yet - will add after populating defaults
   ```

3. **Modify tickets table**
   ```sql
   -- status already stored as TEXT, no schema change needed
   -- but validation logic changes
   ```

### Phase 2: Data Migration

1. **Create default workflow for each organization**
   ```python
   for org in organizations:
     create_workflow(
       organization_id=org.id,
       name="Default Workflow",
       description="Standard workflow with TODO, IN_PROGRESS, and DONE statuses",
       statuses=["TODO", "IN_PROGRESS", "DONE"],
       is_default=True
     )
   ```

2. **Update all projects to reference default workflow**
   ```python
   for project in projects:
     default_workflow = get_default_workflow(project.organization_id)
     project.workflow_id = default_workflow.id
   ```

3. **Validate all existing tickets**
   ```python
   for ticket in tickets:
     project = get_project(ticket.project_id)
     workflow = get_workflow(project.workflow_id)
     assert ticket.status in workflow.statuses, \
       f"Ticket {ticket.id} has invalid status {ticket.status}"
   ```

4. **Add FK constraint**
   ```sql
   -- After all projects have valid workflow_id
   CREATE INDEX idx_projects_workflow ON projects(workflow_id)
   ```

### Phase 3: Code Migration

1. **Update domain models**
   - Change TicketStatus from Enum to string with validation
   - Add Workflow, WorkflowData, WorkflowCreateCommand, etc.
   - Add workflow_id to Project model
   - Update all command models

2. **Update validation logic**
   - Replace enum validation with workflow-based validation
   - Add workflow retrieval for status validation

3. **Add workflow repository layer**
   - WorkflowRepository with CRUD operations
   - Validation for workflow operations

4. **Add workflow API endpoints**
   - GET/POST/PUT/DELETE /api/workflows

5. **Update project API**
   - Accept workflow_id on create/update
   - Validate workflow compatibility when changing

6. **Update ticket API**
   - Validate status against project's workflow
   - Update error messages to include valid statuses

---

## Validation Rules

### Workflow Creation/Update

1. **Name validation**
   - Required, 1-255 characters
   - No uniqueness constraint (multiple workflows can have same name)

2. **Statuses validation**
   - Required, non-empty array
   - Each status must match `^[A-Z0-9_-]+$`
   - No duplicate statuses
   - Recommended: at least 1 status (enforced)

3. **Organization scoping**
   - workflow.organization_id must match user's organization (or user is Super Admin)
   - Cannot reference workflows from other orgs

### Workflow Deletion

1. **Cannot delete if in use**
   - Check if any projects reference this workflow
   - Return 400 with count of affected projects

2. **Cannot delete default workflow**
   - is_default=true workflows cannot be deleted
   - Return 400 with clear error

### Workflow Update - Breaking Changes

1. **Removing statuses**
   - Check if any tickets in projects using this workflow have the status being removed
   - If yes: return 400 with:
     - Count of affected tickets
     - List of affected statuses
     - Suggestion to update tickets first
   - If no: allow update

2. **Adding statuses**
   - Always allowed (non-breaking change)

### Project Workflow Change

1. **Changing project.workflow_id**
   - Get all tickets in project
   - For each ticket, check if ticket.status is in new_workflow.statuses
   - If any incompatible: return 400 with:
     - List of tickets with incompatible statuses
     - Suggestion to fix tickets first
   - If all compatible: allow update

### Ticket Operations

1. **Creating ticket**
   - Get project's workflow (via workflow_id or org default)
   - If status provided: validate against workflow.statuses
   - If status not provided: default to workflow.statuses[0]

2. **Updating ticket status**
   - Get project's workflow
   - Validate new_status in workflow.statuses
   - Return 422 with valid statuses if invalid

3. **Moving ticket between projects**
   - Get target project's workflow
   - Validate ticket.status in target_workflow.statuses
   - Return 400 with valid statuses if invalid

---

## API Changes

### New Endpoints

```
POST   /api/workflows              # Create workflow (PM+)
GET    /api/workflows              # List workflows in org (all users)
GET    /api/workflows/{id}         # Get workflow (all users)
PUT    /api/workflows/{id}         # Update workflow (PM+)
DELETE /api/workflows/{id}         # Delete workflow (Admin+)
```

### Modified Endpoints

```
POST   /api/projects               # Accept optional workflow_id
PUT    /api/projects/{id}          # Accept optional workflow_id
GET    /api/projects/{id}          # Return workflow_id
GET    /api/projects               # Return workflow_id for each

POST   /api/tickets                # Validate status against workflow
PUT    /api/tickets/{id}/status    # Validate status against workflow
PUT    /api/tickets/{id}/project   # Validate status compatibility
```

### Error Response Changes

**Before:**
```json
{
  "detail": "Invalid status value"
}
```

**After:**
```json
{
  "detail": "Invalid status 'CUSTOM_STATUS'. Valid statuses for this project: TODO, IN_PROGRESS, DONE"
}
```

---

## Backward Compatibility

### Existing API Clients

1. **Ticket creation without status**
   - BEFORE: defaults to "TODO"
   - AFTER: defaults to workflow.statuses[0]
   - For default workflow: same behavior (statuses[0] = "TODO")
   - For custom workflows: different default possible

2. **Ticket status values**
   - BEFORE: enum values TODO/IN_PROGRESS/DONE
   - AFTER: string values, validated against workflow
   - Default workflow maintains same values
   - Custom workflows can have different values

3. **Project creation**
   - BEFORE: no workflow_id
   - AFTER: workflow_id defaults to org's default workflow
   - Behavior unchanged (projects still use TODO/IN_PROGRESS/DONE by default)

### Database

1. **Tickets table**
   - status already stored as TEXT (not enum)
   - No schema change needed
   - Validation changes from enum to dynamic

2. **Projects table**
   - Adds workflow_id column (nullable)
   - Null means use org default (backward compatible)

---

## Activity Logging

### New Action Types

Add to ActionType enum:
```python
WORKFLOW_CREATED = "workflow_created"
WORKFLOW_UPDATED = "workflow_updated"
WORKFLOW_DELETED = "workflow_deleted"
```

### New Activity Log Events

1. **Workflow Operations**
   - Create workflow → WORKFLOW_CREATED
   - Update workflow → WORKFLOW_UPDATED
   - Delete workflow → WORKFLOW_DELETED

2. **Project Workflow Changes**
   - Update project.workflow_id → PROJECT_UPDATED
   - Include old_workflow_id and new_workflow_id in details

---

## Testing Strategy

### Unit Tests

1. **Workflow Repository**
   - CRUD operations
   - Validation (statuses format, uniqueness, etc.)
   - Organization scoping
   - Default workflow handling

2. **Workflow Validation**
   - Status format validation
   - Duplicate status detection
   - Breaking change detection (status removal)

### Integration Tests

1. **Workflow API**
   - Create/read/update/delete workflows
   - Permission checks (PM+ for create/update, Admin+ for delete)
   - Organization scoping
   - Default workflow immutability

2. **Project API**
   - Create/update project with workflow_id
   - Workflow validation
   - Cross-org workflow reference (should fail)
   - Changing workflow with incompatible tickets

3. **Ticket API**
   - Create ticket with workflow validation
   - Update status with workflow validation
   - Move ticket between projects with different workflows
   - Error messages include valid statuses

4. **Migration Tests**
   - Default workflow creation for new orgs
   - Existing tickets remain valid after migration

---

## Potential Issues & Mitigations

### Issue 1: Orphaned Projects
**Problem**: Workflow deleted, projects left with invalid workflow_id
**Mitigation**: Prevent workflow deletion if projects reference it (REQ-WORKFLOW-005)

### Issue 2: Status Mismatch After Workflow Update
**Problem**: Workflow updated to remove status, tickets become invalid
**Mitigation**: Validate workflow updates, prevent breaking changes (REQ-WORKFLOW-009)

### Issue 3: Circular Dependencies
**Problem**: Can't update workflow because tickets exist, can't update tickets because workflow invalid
**Mitigation**: Workflow updates that ADD statuses always allowed; only REMOVING statuses is validated

### Issue 4: Performance
**Problem**: Every ticket operation now requires workflow lookup
**Mitigation**:
- Cache workflows in memory
- Add database indexes on workflow_id
- Consider denormalizing workflow.statuses to project table

### Issue 5: Default Workflow Edge Cases
**Problem**: What if org's default workflow is deleted?
**Mitigation**: Prevent deletion of is_default=true workflows (constraint + validation)

### Issue 6: Migration Failure
**Problem**: Existing tickets have invalid statuses (data corruption)
**Mitigation**:
- Validation script before migration
- Rollback plan if validation fails
- Migration in transaction

---

## Performance Considerations

### Database Queries

1. **Workflow Lookup for Ticket Operations**
   ```python
   # Before: No lookup needed (enum validation)
   # After: Need to fetch project → workflow → statuses

   # Optimization: Cache workflows
   workflow_cache = {}  # org_id → {workflow_id → workflow}
   ```

2. **Indexes Needed**
   ```sql
   CREATE INDEX idx_workflows_org ON workflows(organization_id)
   CREATE INDEX idx_projects_workflow ON projects(workflow_id)
   CREATE INDEX idx_workflows_default ON workflows(organization_id, is_default)
   ```

### Caching Strategy

1. **Workflow Cache**
   - Cache workflows by organization
   - Invalidate on workflow update/delete
   - TTL: 5-10 minutes

2. **Project Workflow Cache**
   - Cache project.workflow_id
   - Invalidate on project update
   - TTL: 5-10 minutes

---

## Rollback Plan

### If Migration Fails

1. **Schema Rollback**
   ```sql
   ALTER TABLE projects DROP COLUMN workflow_id
   DROP TABLE workflows
   ```

2. **Code Rollback**
   - Revert to enum-based status validation
   - Remove workflow endpoints
   - Restore previous ticket validation logic

3. **Data Integrity**
   - No ticket data changes (status remains TEXT)
   - Projects lose workflow_id column (but was optional anyway)
   - Workflow data deleted (but was new)

### Rollback Risks

- Low risk: workflow_id was optional for projects
- No data loss for tickets (status field unchanged)
- Organizations can recreate workflows if needed

---

## Timeline Estimate

1. **Specification Complete**: ✅ Done
2. **Data Model & Migration**: 2-3 days
3. **Workflow Repository & API**: 2-3 days
4. **Project Integration**: 1-2 days
5. **Ticket Validation Updates**: 2-3 days
6. **Testing & Validation**: 2-3 days
7. **Documentation**: 1 day

**Total**: 10-15 days for complete implementation

---

## Open Questions

1. **Should workflow statuses have ordering?**
   - Pro: Could show in specific order in UI
   - Con: Adds complexity
   - Decision: Not in V1, use array order for now

2. **Should we support status transitions/rules?**
   - Example: Can't go from TODO directly to DONE
   - Decision: Not in V1, all transitions allowed (like current behavior)

3. **Should status names be case-insensitive?**
   - Pro: User-friendly
   - Con: Complexity in validation/comparison
   - Decision: Case-sensitive (enforce uppercase via regex pattern)

4. **Should we support workflow templates/presets?**
   - Example: "Kanban", "Scrum", "Bug Tracking"
   - Decision: Not in V1, users create from scratch

5. **Should we allow renaming statuses in-place?**
   - Pro: Convenience
   - Con: Affects all existing tickets
   - Decision: Not in V1, use add-then-remove approach
