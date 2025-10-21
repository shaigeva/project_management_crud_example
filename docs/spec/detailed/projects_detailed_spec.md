# Projects: Detailed Specification

**Status**: 🔴 0/8 requirements implemented (0%)
**Parent**: [Main Spec](../main_spec.md#feature-project-management)
**Last Updated**: 2024-01-20

## Rationale

Projects are the primary organizational container for tasks and work. Users need to:
- Create projects to organize their work
- View project details to understand scope and status
- Update projects as requirements change
- Delete projects that are cancelled or completed

This spec defines the **externally observable behavior** of project management, focusing on what users can verify through the API rather than internal implementation details.

---

## REQ-PROJ-001: Create project and verify persistence
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user creates a project with valid data (name and optional description)

### Observable Behavior
- User receives a response containing the created project with these fields:
  - `id`: Unique identifier (non-empty string)
  - `name`: The provided project name
  - `description`: The provided description (or null if not provided)
  - `created_at`: Timestamp of creation
  - `updated_at`: Timestamp of last update (same as created_at initially)
- After creation, GET /projects/{id} returns the same project
- After creation, GET /projects includes the new project in the list
- All project data matches what was submitted

### Test Specification

1. **Test**: `test_after_create_project_get_by_id_returns_the_project`
   - **Verifies**: Created project is retrievable by ID
   - **Steps**:
     - POST /projects with `{"name": "Test Project", "description": "Test"}`
     - Capture `id` from response
     - GET /projects/{id}
     - Assert response status 200
     - Assert returned project has correct name, description
     - Assert id, created_at, updated_at are present

2. **Test**: `test_after_create_project_appears_in_list`
   - **Verifies**: Created project appears in full project list
   - **Steps**:
     - POST /projects with unique name "Unique Project XYZ"
     - GET /projects
     - Assert response contains project with name "Unique Project XYZ"

3. **Test**: `test_create_project_without_description_succeeds`
   - **Verifies**: Description is optional
   - **Steps**:
     - POST /projects with only `{"name": "No Desc Project"}`
     - Assert response status 201
     - Assert description is null in response
     - GET /projects/{id}
     - Assert description is null

4. **Test**: `test_create_project_returns_all_required_fields`
   - **Verifies**: Response includes all expected fields
   - **Steps**:
     - POST /projects
     - Assert response contains: id, name, description, created_at, updated_at
     - Assert id is non-empty string
     - Assert created_at is valid ISO datetime
     - Assert updated_at equals created_at

### Edge Cases to Test

- Creating project with maximum length name (255 characters)
- Creating project with minimum length name (1 character)
- Creating project with special characters in name: `!@#$%^&*()`
- Creating project with unicode characters: "Proyecto Español 日本"
- Creating multiple projects with identical names (should all succeed)

---

## REQ-PROJ-002: Retrieve project by ID
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific project by ID

### Observable Behavior
- If project exists: Returns 200 with complete project data
- If project doesn't exist: Returns 404 with error message
- Returned data matches what was stored during creation

### Test Specification

1. **Test**: `test_get_existing_project_by_id_returns_project`
   - **Verifies**: Existing project is returned with correct data
   - **Steps**:
     - Create project via POST
     - GET /projects/{id}
     - Assert status 200
     - Assert data matches creation data

2. **Test**: `test_get_non_existent_project_returns_404`
   - **Verifies**: Missing project returns appropriate error
   - **Steps**:
     - GET /projects/non-existent-id-12345
     - Assert status 404
     - Assert response contains error detail

---

## REQ-PROJ-003: List all projects
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests the list of all projects

### Observable Behavior
- Returns 200 with array of all projects
- If no projects exist, returns empty array
- Each project in list has same structure as individual GET
- Order is consistent (newest first recommended)

### Test Specification

1. **Test**: `test_get_all_projects_when_empty_returns_empty_array`
   - **Verifies**: Empty list before any projects created
   - **Steps**:
     - GET /projects
     - Assert status 200
     - Assert response is empty array []

2. **Test**: `test_get_all_projects_returns_all_created_projects`
   - **Verifies**: All created projects appear in list
   - **Steps**:
     - Create 3 projects with unique names
     - GET /projects
     - Assert response contains all 3 projects
     - Assert each has all required fields

3. **Test**: `test_get_all_projects_after_delete_excludes_deleted`
   - **Verifies**: Deleted projects don't appear in list
   - **Steps**:
     - Create project A
     - Create project B
     - DELETE project A
     - GET /projects
     - Assert list contains only project B

---

## REQ-PROJ-007: Handle validation errors
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user provides invalid data during project creation or update

### Observable Behavior
- Returns 400 or 422 status code
- Response includes clear error message explaining validation failure
- No project is created/modified
- Subsequent GET confirms no change occurred

### Test Specification

1. **Test**: `test_create_project_without_name_returns_validation_error`
   - **Verifies**: Name is required
   - **Steps**:
     - POST /projects with `{"description": "No name"}`
     - Assert status 400 or 422
     - Assert error message mentions "name" field
     - GET /projects
     - Assert no project was created

2. **Test**: `test_create_project_with_empty_name_returns_validation_error`
   - **Verifies**: Name cannot be empty string
   - **Steps**:
     - POST /projects with `{"name": ""}`
     - Assert status 400 or 422
     - Assert error indicates name is required/invalid

3. **Test**: `test_create_project_with_name_too_long_returns_validation_error`
   - **Verifies**: Name length is limited
   - **Steps**:
     - POST /projects with name of 1000 characters
     - Assert status 400 or 422
     - Assert error mentions name length

4. **Test**: `test_create_project_with_invalid_data_type_returns_validation_error`
   - **Verifies**: Field types are validated
   - **Steps**:
     - POST /projects with `{"name": 12345}` (number instead of string)
     - Assert status 400 or 422
     - Assert error mentions type validation

---

## Implementation Notes

**DO:**
- Test all behaviors through HTTP API endpoints
- Verify state changes by subsequent GET requests
- Test complete user workflows (create → retrieve → verify)
- Cover all specified edge cases

**DON'T:**
- Query database directly in tests
- Test internal implementation details (table names, ORM models)
- Assume specific database structure
- Skip edge cases "because they're unlikely"

**Remember**: If a user cannot observe it through the API, don't test it directly.
Test the externally observable consequences instead.
