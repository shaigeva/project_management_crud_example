# Current Task List - Projects CRUD

**Created**: 2025-01-25
**Spec Reference**: [Projects](../spec/detailed/projects_detailed_spec.md)

---

## Overview

Implement CRUD operations for Projects within organizations. Projects are the primary organizational container for tickets. This implementation will also enable testing of organization-scoped data isolation (REQ-ORG-005, REQ-ORG-006).

**Scope**: REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003, REQ-PROJ-007

**Note**: Projects are organization-scoped. Each project belongs to an organization, and users can only access projects within their organization (except Super Admins).

---

## Task 1: Project domain models and validation
**Status**: ⏳ Pending
**Implements**: Foundation for REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003, REQ-PROJ-007

### Description
Create domain models for Projects with validation rules.

### Requirements from Spec
- Project data structure (name, description, organization_id, timestamps)
- Validation: name required (1-255 chars), description optional (max 1000 chars)
- ProjectCreateCommand and ProjectUpdateCommand
- Organization scoping (all projects belong to an organization)

### Implementation Checklist
- [ ] Create `Project` domain model (id, name, description, organization_id, created_at, updated_at)
- [ ] Create `ProjectData` model for input validation (name, description)
- [ ] Create `ProjectCreateCommand` model (includes organization_id)
- [ ] Create `ProjectUpdateCommand` model (partial updates)
- [ ] Add validation rules (name length, required fields, description max length)
- [ ] Write domain validation tests in `tests/domain/test_project_models.py`

---

## Task 2: Project repository layer
**Status**: ⏳ Pending
**Implements**: Foundation for REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003
**Dependencies**: Task 1

### Description
Implement repository methods for Project CRUD operations with organization scoping.

### Requirements from Spec
- Create project within organization
- Retrieve project by ID
- List projects (filterable by organization)
- Update project details
- Delete project (for testing, not exposed in V1 API)
- Proper ORM-to-domain conversion

### Implementation Checklist
- [ ] Create `ProjectORM` model in `orm_data_models.py`
- [ ] Add foreign key to OrganizationORM
- [ ] Create converter `orm_project_to_domain_project()`
- [ ] Add `Projects` nested class to Repository
- [ ] Implement `repo.projects.create()` method
- [ ] Implement `repo.projects.get_by_id()` method
- [ ] Implement `repo.projects.get_by_organization_id()` method
- [ ] Implement `repo.projects.get_all()` method (for Super Admin)
- [ ] Implement `repo.projects.update()` method
- [ ] Implement `repo.projects.delete()` method (for cleanup)
- [ ] Write repository tests in `tests/dal/test_project_repository.py`

---

## Task 3: Project API endpoints with organization scoping
**Status**: ⏳ Pending
**Implements**: REQ-PROJ-001, REQ-PROJ-002, REQ-PROJ-003, REQ-PROJ-007
**Dependencies**: Task 1, Task 2

### Description
Create REST API endpoints for Projects with organization-based data isolation.

### Requirements from Spec
- POST /api/projects - Create project (auto-assign to user's organization)
- GET /api/projects/{id} - Get project (only if in user's organization)
- GET /api/projects - List projects (filtered by user's organization)
- PUT /api/projects/{id} - Update project (only if in user's organization)
- Enforce organization-scoped access (except Super Admin)
- Return 404 for cross-organization access (not 403, to avoid leaking existence)
- Proper error responses (404, 400, 422)

### Implementation Checklist
- [ ] Create `routers/project_api.py` with router setup
- [ ] Implement POST /api/projects (auto-set organization_id from current_user)
- [ ] Implement GET /api/projects/{id} (check organization_id matches)
- [ ] Implement GET /api/projects (filter by user's organization_id)
- [ ] Implement PUT /api/projects/{id} (check organization_id matches)
- [ ] Add organization-scoped permission checks
- [ ] Return 404 (not 403) for cross-organization access attempts
- [ ] Handle validation errors with 422 status
- [ ] Include router in `app.py`
- [ ] Write comprehensive API tests in `tests/api/test_project_api.py`

---

## Task 4: Organization data isolation validation
**Status**: ⏳ Pending
**Implements**: REQ-ORG-005, REQ-ORG-006 (partial - for projects only)
**Dependencies**: Task 3

### Description
Validate that organization data isolation works correctly for projects. Users from different organizations cannot access each other's projects.

### Requirements from Spec
- Users in Org A cannot see projects from Org B
- Attempting to access another org's project by ID returns 404
- List endpoints are automatically filtered by user's organization
- Super Admins can access all organizations' projects
- Error messages do not leak cross-organization information

### Implementation Checklist
- [ ] Test user from Org A cannot access Org B's project by ID (returns 404)
- [ ] Test user from Org A's list doesn't include Org B's projects
- [ ] Test Super Admin can access all organizations' projects
- [ ] Test Super Admin's list includes all projects
- [ ] Test creating project assigns to user's organization automatically
- [ ] Test users cannot create projects in other organizations
- [ ] Test error messages don't reveal existence of other orgs' data
- [ ] Complete workflow: create in Org A, verify isolated from Org B
- [ ] Run full validation suite: `./devtools/run_all_agent_validations.sh`

---

## Completion Criteria

### All Tasks Complete
- [ ] All tasks marked ✅
- [ ] All tests passing (zero failures, zero errors)
- [ ] Zero linting errors
- [ ] Zero type checking errors
- [ ] Code formatted correctly

### Spec Updates
- [ ] REQ-PROJ-001 marked ✅ in `projects_detailed_spec.md`
- [ ] REQ-PROJ-002 marked ✅ in `projects_detailed_spec.md`
- [ ] REQ-PROJ-003 marked ✅ in `projects_detailed_spec.md`
- [ ] REQ-PROJ-007 marked ✅ in `projects_detailed_spec.md`
- [ ] REQ-ORG-005 marked ✅ in `organizations_detailed_spec.md` (partial - projects only)
- [ ] REQ-ORG-006 marked ✅ in `organizations_detailed_spec.md` (partial - projects only)
- [ ] Feature status updated in `main_spec.md`

### Archival
- [ ] Archive this file to `archive/2025-01-25_projects_crud.md`
- [ ] Clear `current_task_list.md` or create new task list for next feature

---

## Notes

**Organization Scoping**: Unlike Organizations CRUD (which is Super Admin only for create/update), Projects are organization-scoped for all users:
- Users automatically create projects in their own organization
- Users can only see/update projects in their organization
- Super Admin can access all projects across all organizations

**Data Isolation**: This implementation completes REQ-ORG-005 and REQ-ORG-006 for Projects. Full completion will require implementing the same pattern for Tickets.

**No Delete Endpoint**: Projects can be deleted via repository (for testing), but there's no DELETE endpoint in the V1 API. Projects should be archived/deactivated instead (future feature).

**Permission Model**: For V1, all authenticated users within an organization can create/update projects. Future versions may restrict to Project Manager role and above.
