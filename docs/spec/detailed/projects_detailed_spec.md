# Projects: Detailed Specification

**Status**: 🟡 6/7 requirements implemented (86%)
**Parent**: [Main Spec](../main_spec.md#feature-projects)
**Last Updated**: 2025-01-26

**Note**: This detailed spec covers requirements REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003, REQ-PROJ-007, REQ-PROJ-009, and REQ-PROJ-010 (the core CRUD behaviors, validation, filtering, and archival). Requirements REQ-PROJ-004 (update), REQ-PROJ-005 (delete), and REQ-PROJ-006 (organization scoping) are implemented but documented through tests rather than separate spec sections.

## Rationale

Projects are the primary organizational container for tasks and work. Users need to:
- Create projects to organize their work
- View project details to understand scope and status
- Update projects as requirements change
- Delete projects that are cancelled or completed

This spec defines the **externally observable behavior** of project management, focusing on what users can verify through the API rather than internal implementation details.

---

## REQ-PROJ-001: Create project and verify persistence
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user creates a project with valid data (name and optional description)

### Observable Behavior
User can create a project via API and subsequently verify its existence and correct data through API calls.

### Acceptance Criteria
- POST /projects with valid data returns 201 response
- Response contains created project with all fields:
  - `id`: Unique identifier (non-empty string)
  - `name`: The provided project name
  - `description`: The provided description (or null if not provided)
  - `created_at`: Timestamp of creation
  - `updated_at`: Timestamp of last update (initially same as created_at)
- After creation, GET /projects/{id} returns the same project
- Returned data from GET matches what was submitted
- After creation, GET /projects includes the new project in the list
- Description field is optional (can be omitted)
- Creating project without description succeeds with description=null

### Edge Cases
- Maximum length name (255 characters)
- Minimum length name (1 character)
- Special characters in name: `!@#$%^&*()`
- Unicode characters: "Proyecto Español 日本"
- Multiple projects with identical names (all succeed)
- Name-only project (no description field)

---

## REQ-PROJ-002: Retrieve project by ID
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific project by ID

### Observable Behavior
User can retrieve a specific project by its ID or receive appropriate error if not found.

### Acceptance Criteria
- GET /projects/{id} for existing project returns 200 with project data
- Returned data matches what was stored during creation
- GET /projects/{id} for non-existent ID returns 404
- 404 response includes error message/detail field
- Multiple GET requests for same ID return consistent data

### Edge Cases
- Non-existent project IDs
- Malformed IDs (if applicable)

---

## REQ-PROJ-003: List all projects
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests the list of all projects

### Observable Behavior
User can retrieve a list of all projects through the API.

### Acceptance Criteria
- GET /projects returns 200 with array of all projects
- If no projects exist, returns empty array []
- Each project in list has same structure as individual GET response
- All created projects appear in the list
- Deleted projects do not appear in the list
- Order is consistent across requests

### Edge Cases
- Empty database (no projects)
- Large number of projects
- After creating/deleting projects

---

## REQ-PROJ-007: Handle validation errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user provides invalid data during project creation or update

### Observable Behavior
User receives clear error messages when providing invalid data, and no invalid data is persisted.

### Acceptance Criteria
- POST /projects with invalid data returns 400 or 422 status
- Response includes clear error message explaining what is invalid
- Error message identifies which field has the problem
- No project is created when validation fails
- Subsequent GET /projects confirms nothing was created
- Empty name is rejected (required field)
- Name exceeding max length (255 chars) is rejected
- Invalid data types are rejected (e.g., number for name field)

### Edge Cases
- Missing required field (name)
- Empty string for name
- Name too long (>255 characters)
- Wrong data type for field
- Invalid characters (if any restrictions exist)

---

## REQ-PROJ-009: Filter and search projects
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user lists projects, they may want to filter by name or active status

### Observable Behavior
Users can filter project lists using query parameters for name substring search and active status filtering.

### Acceptance Criteria
- GET /projects?name=substring returns projects containing substring in name (case-insensitive)
- GET /projects?is_active=true returns only active projects
- GET /projects?is_active=false returns only inactive projects
- GET /projects?name=substring&is_active=true combines both filters
- Name search is case-insensitive (backend, BACKEND, Backend all match "Backend API")
- Filters respect organization scoping (users only see projects in their org)
- Super Admin filters work across all organizations
- No matches returns empty array []
- Filters work with all role permissions (all roles can filter within their access)

### Edge Cases
- Filter with no matches returns empty array
- Empty name parameter (treated as no filter)
- Name with special characters
- Multiple projects matching filter
- Filter combining multiple criteria

---

## REQ-PROJ-010: Archive and unarchive projects (soft delete)
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When users want to remove projects without permanently deleting data, they can archive projects for soft deletion and later unarchive to restore them

### Observable Behavior
Projects can be archived (soft deleted) and unarchived (restored). Archived projects are hidden from default listings but can be included explicitly.

### Acceptance Criteria
**Archive Operation**:
- PATCH /api/projects/{id}/archive sets is_archived=true and archived_at=timestamp
- Archived projects do not appear in GET /api/projects by default
- GET /api/projects?include_archived=true includes archived projects in results
- Admin and Project Manager can archive projects in their organization
- Super Admin can archive projects in any organization
- Returns 403 if user lacks archive permission
- Returns 404 if project doesn't exist

**Unarchive Operation**:
- PATCH /api/projects/{id}/unarchive sets is_archived=false and archived_at=null
- Unarchived projects appear in default GET /api/projects listings
- Only Admin and Super Admin can unarchive projects
- Project Managers cannot unarchive (stricter permission than archive)
- Returns 403 if user lacks unarchive permission
- Returns 404 if project doesn't exist

**List Filtering**:
- GET /api/projects excludes archived by default
- GET /api/projects?include_archived=true shows both active and archived
- include_archived parameter works with name and is_active filters
- Organization scoping applies to archived projects

**Data Integrity**:
- Archive operation is idempotent (archiving archived project succeeds)
- Unarchive operation is idempotent (unarchiving active project succeeds)
- Hard delete (DELETE /api/projects/{id}) remains available for permanent removal

### Edge Cases
- Archive already archived project (succeeds, updates timestamp)
- Unarchive already active project (succeeds, no change)
- Filter combinations: include_archived with name/is_active filters
- Cross-organization archive attempts (403 forbidden)
- Future: Prevent ticket creation in archived projects (not yet implemented)

---

## REQ-PROJ-011: Projects reference workflows
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When creating or updating a project, users can optionally specify which workflow the project should use for its tickets

### Observable Behavior
Projects can reference a workflow, and tickets in that project must have statuses valid for the project's workflow.

### Acceptance Criteria
**Project Creation with Workflow**:
- POST /api/projects can include optional `workflow_id` parameter
- If workflow_id provided:
  - Workflow must exist in the same organization
  - Workflow from different organization returns 403
  - Non-existent workflow returns 404
  - Response includes workflow_id in project data
- If workflow_id not provided:
  - Project uses organization's default workflow
  - Response includes workflow_id set to default workflow's ID
- GET /api/projects/{id} returns project with workflow_id field

**Project Update with Workflow**:
- PUT /api/projects/{id} can update workflow_id
- Changing workflow validates:
  - New workflow exists in same organization
  - All existing tickets in project have statuses valid in new workflow
  - If any ticket has invalid status for new workflow, update fails with 400
  - Error message lists which tickets/statuses are incompatible
- Changing to null/omitting workflow_id sets to organization's default workflow
- Successful workflow change updates project and returns updated project data

**Project Retrieval**:
- GET /api/projects/{id} response includes:
  - `workflow_id`: ID of the workflow this project uses
  - All existing fields (id, name, description, organization_id, is_archived, etc.)
- GET /api/projects list response includes workflow_id for each project

**Workflow Association**:
- Projects can only reference workflows from their organization
- Multiple projects can use the same workflow
- Default workflow is used if workflow_id is null or not specified
- Project's workflow determines valid statuses for its tickets

### Edge Cases
- Creating project without workflow_id (uses default)
- Creating project with explicit workflow_id
- Creating project with non-existent workflow_id (404)
- Creating project with workflow from different org (403)
- Updating project to change workflow (validates ticket compatibility)
- Updating project to workflow that's incompatible with existing tickets (fails)
- Updating project to null workflow_id (uses default)
- Deleting workflow that projects reference (see REQ-WORKFLOW-005 - should fail)
