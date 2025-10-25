# Projects: Detailed Specification

**Status**: 🟢 5/5 requirements implemented (100%)
**Parent**: [Main Spec](../main_spec.md#feature-projects)
**Last Updated**: 2025-01-26

**Note**: This detailed spec covers requirements REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003, REQ-PROJ-007, and REQ-PROJ-009 (the core CRUD behaviors, validation, and filtering). Requirements REQ-PROJ-004 (update), REQ-PROJ-005 (delete), and REQ-PROJ-006 (organization scoping) are implemented but documented through tests rather than separate spec sections. REQ-PROJ-010 (archive) is pending future implementation.

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
