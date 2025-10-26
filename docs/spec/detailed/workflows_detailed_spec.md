# Workflows: Detailed Specification

**Status**: 🔴 0/10 requirements implemented (0%)
**Parent**: [Main Spec](../main_spec.md#feature-custom-workflows)
**Last Updated**: 2025-01-26

## Rationale

Different teams and organizations have different processes for tracking work. While the default TODO/IN_PROGRESS/DONE workflow works for many teams, others need custom statuses that match their specific processes (e.g., "BACKLOG", "CODE_REVIEW", "QA", "DEPLOYED" for engineering teams, or "NEW", "TRIAGED", "ASSIGNED", "RESOLVED", "CLOSED" for support teams).

Workflows define the set of valid statuses that tickets can have within a project. This spec defines the **externally observable behavior** of workflow management.

### Key Design Decisions

1. **Scope**: Workflows are organization-scoped (each org defines its own workflows)
2. **Default Workflow**: Each organization has a default workflow with statuses ["TODO", "IN_PROGRESS", "DONE"] for backward compatibility
3. **Project Association**: Projects optionally reference a workflow; if not specified, they use the org's default workflow
4. **Status Transitions**: V1 allows all status transitions (no transition rules); future versions may add transition constraints
5. **Changing Workflows**: Projects cannot change workflows if they have tickets with statuses incompatible with the target workflow

---

## REQ-WORKFLOW-001: Create workflow in organization
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user with Project Manager or higher role creates a custom workflow with a name and list of statuses

### Observable Behavior
User can create a workflow via API and subsequently verify its existence and correct data through API calls.

### Acceptance Criteria
- POST /api/workflows with valid data returns 201 response
- Response contains created workflow with all fields:
  - `id`: Unique identifier (non-empty string)
  - `name`: The provided workflow name
  - `description`: The provided description (or null if not provided)
  - `statuses`: Array of status strings (non-empty)
  - `organization_id`: The organization this workflow belongs to
  - `is_default`: Boolean (false for custom workflows)
  - `created_at`: Timestamp of creation
  - `updated_at`: Timestamp of last update
- After creation, GET /api/workflows/{id} returns the same workflow
- After creation, GET /api/workflows includes the new workflow in the list
- Statuses array must contain at least one status
- Status names are case-sensitive strings
- Status names can contain letters, numbers, underscores, and hyphens
- Duplicate status names within the same workflow are not allowed
- Only users with Project Manager, Admin, or Super Admin roles can create workflows
- Users with Write or Read roles receive 403 error
- Workflow is automatically scoped to user's organization (cannot create in different org)

### Edge Cases
- Maximum workflow name length (255 characters)
- Minimum workflow name (1 character)
- Single status in statuses array (minimum valid workflow)
- Many statuses (e.g., 20+ statuses)
- Status names with special characters: "IN-PROGRESS", "CODE_REVIEW", "QA_TESTING"
- Empty statuses array (validation error)
- Duplicate status names (validation error)
- Creating workflow without description succeeds
- Two workflows with same name in same org (allowed - names don't have to be unique)

---

## REQ-WORKFLOW-002: Retrieve workflow by ID
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific workflow by ID

### Observable Behavior
User can retrieve a specific workflow by its ID or receive appropriate error if not found or unauthorized.

### Acceptance Criteria
- GET /api/workflows/{id} for existing workflow returns 200 with workflow data
- Returned data matches what was stored during creation
- GET /api/workflows/{id} for non-existent ID returns 404
- GET /api/workflows/{id} for workflow in different organization returns 403 (non-Super Admin)
- Super Admin can retrieve workflows from any organization
- 404 response includes error message/detail field
- Multiple GET requests for same ID return consistent data
- Response includes all fields: id, name, description, statuses, organization_id, is_default, created_at, updated_at

### Edge Cases
- Non-existent workflow IDs
- Workflows from different organizations
- Default workflow retrieval
- Super Admin cross-org access

---

## REQ-WORKFLOW-003: List workflows in organization
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests the list of workflows

### Observable Behavior
User can retrieve a list of all workflows in their organization through the API.

### Acceptance Criteria
- GET /api/workflows returns 200 with array of workflows
- If no custom workflows exist, returns array with only the default workflow
- Each workflow in list has same structure as individual GET response
- All workflows in user's organization appear in the list (including default)
- Workflows from other organizations do not appear (for non-Super Admin)
- Super Admin sees all workflows across all organizations
- List includes both custom workflows and default workflow
- Default workflow is marked with is_default=true
- Order is consistent across requests (sorted by created_at descending)

### Edge Cases
- Organization with only default workflow (returns array with 1 item)
- Organization with many custom workflows
- Super Admin viewing all workflows

---

## REQ-WORKFLOW-004: Update workflow details
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user with appropriate permissions updates a workflow's name, description, or statuses

### Observable Behavior
User can update workflow fields via API, with changes persisted and verifiable.

### Acceptance Criteria
- PUT /api/workflows/{id} with update data returns 200 with updated workflow
- Can update name, description, or statuses independently
- Can update multiple fields simultaneously
- Cannot update id, organization_id, is_default, created_at
- Updated workflow has new updated_at timestamp
- Subsequent GET shows updated values
- Updating non-existent workflow returns 404
- Updating workflow in different org returns 403 (non-Super Admin)
- Only Project Manager, Admin, or Super Admin can update workflows
- Write/Read users receive 403 error
- When updating statuses, new status list must be non-empty
- When updating statuses, duplicate status names are not allowed

### Edge Cases
- Partial updates (only one field)
- Updating to empty description (clearing field)
- Adding new statuses to existing workflow
- Removing statuses from workflow (see REQ-WORKFLOW-009 for validation)
- Renaming existing statuses
- Validation failures on update

---

## REQ-WORKFLOW-005: Delete workflow
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user attempts to delete a workflow

### Observable Behavior
User can delete unused workflows with appropriate permissions, but cannot delete workflows that are in use.

### Acceptance Criteria
- DELETE /api/workflows/{id} returns 204 (no content) if successful
- After deletion, GET /api/workflows/{id} returns 404
- Deleted workflow does not appear in workflow list
- Deleting non-existent workflow returns 404
- Only Admin or Super Admin can delete workflows (Project Manager cannot)
- Write/Read users receive 403 error
- Cannot delete workflow if any projects reference it (returns 400 with error detail)
- Cannot delete default workflow (is_default=true) - returns 400
- Error message for in-use workflow indicates which/how many projects are using it
- Deleting workflow in different org returns 403 (non-Super Admin)

### Edge Cases
- Deleting workflow with active projects (fails)
- Deleting workflow with archived projects (fails - projects still reference it)
- Deleting unused workflow (succeeds)
- Deleting default workflow (fails)
- Permission checks (only Admin+)

---

## REQ-WORKFLOW-006: Default workflow exists for each organization
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an organization is created or when listing workflows

### Observable Behavior
Each organization automatically has a default workflow that cannot be deleted.

### Acceptance Criteria
- When organization is created, a default workflow is automatically created
- Default workflow has:
  - name: "Default Workflow"
  - description: "Standard workflow with TODO, IN_PROGRESS, and DONE statuses"
  - statuses: ["TODO", "IN_PROGRESS", "DONE"]
  - is_default: true
  - organization_id: the organization's ID
- GET /api/workflows always includes the default workflow
- Default workflow cannot be deleted (DELETE returns 400)
- Default workflow can be updated (name, description, statuses) but is_default cannot be changed
- Each organization has exactly one default workflow (is_default=true)
- Projects created without workflow_id automatically use the default workflow

### Edge Cases
- Organization creation triggers default workflow creation
- Cannot change is_default flag on any workflow
- Cannot create second default workflow
- Updating default workflow's statuses affects projects using it

---

## REQ-WORKFLOW-007: Workflow validation
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When creating or updating a workflow with invalid data

### Observable Behavior
Clear validation error messages for invalid workflow data.

### Acceptance Criteria
- POST/PUT with empty name returns 422 validation error
- POST/PUT with name > 255 chars returns 422 validation error
- POST/PUT with description > 1000 chars returns 422 validation error
- POST/PUT with empty statuses array returns 422 validation error
- POST/PUT with duplicate status names returns 422 validation error
- POST/PUT with invalid status names returns 422 validation error
- Status names must match pattern: ^[A-Z0-9_-]+$ (uppercase letters, numbers, underscores, hyphens)
- Error message identifies which field is invalid
- Error message explains what is wrong

### Edge Cases
- Empty statuses array
- Null statuses field
- Status names with lowercase letters (validation error)
- Status names with spaces (validation error)
- Status names with special characters beyond underscore/hyphen
- Duplicate status names (case-sensitive check)

---

## REQ-WORKFLOW-008: Organization scoping
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When accessing workflows across organizations

### Observable Behavior
Users can only access workflows from their organization (except Super Admin).

### Acceptance Criteria
- Users cannot see workflows from other organizations
- Super Admin can see all workflows
- Attempting to access workflow from different org returns 403 (or 404 for GET to prevent information leakage)
- List operations only return workflows from user's organization
- Creating workflow automatically scopes to user's organization
- Cannot create workflow for different organization
- All workflow operations enforce organization boundaries

### Edge Cases
- Cross-organization access attempts
- Super Admin access to all orgs
- Default workflow visibility

---

## REQ-WORKFLOW-009: Cannot update workflow if it breaks existing tickets
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When updating a workflow's statuses in a way that would make existing tickets invalid

### Observable Behavior
System prevents workflow updates that would create invalid ticket states.

### Acceptance Criteria
- PUT /api/workflows/{id} that removes statuses fails with 400 if:
  - Any project using this workflow has tickets with removed statuses
- Error message indicates:
  - How many projects/tickets would become invalid
  - Which status(es) cannot be removed
  - Suggestion to update tickets first
- Workflow updates that add statuses always succeed
- Workflow updates that rename statuses (add new, remove old) follow same validation
- If no tickets would be affected, removing statuses succeeds

### Edge Cases
- Removing status that no tickets use (succeeds)
- Removing status that some tickets use (fails with details)
- Adding new statuses (always succeeds)
- Workflow with no projects using it (all updates succeed)

---

## REQ-WORKFLOW-010: Handle not-found and permission errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When requesting non-existent workflows or accessing without permission

### Observable Behavior
Clear error messages for missing resources and permission issues.

### Acceptance Criteria
- GET /api/workflows/{non-existent-id} returns 404
- 404 response includes detail: "Workflow not found"
- Updating non-existent workflow returns 404
- Deleting non-existent workflow returns 404
- Users without Project Manager+ role get 403 on create/update
- Users without Admin+ role get 403 on delete
- Cross-org access returns 403 (for mutation) or 404 (for GET, to prevent info leakage)
- Error messages are clear and actionable

### Edge Cases
- Non-existent IDs
- Insufficient permissions
- Cross-organization access attempts
