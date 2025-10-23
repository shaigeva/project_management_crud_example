# Current Task List - Organizations CRUD

**Created**: 2025-01-23
**Spec Reference**: [Multi-Tenancy (Organizations)](../spec/detailed/organizations_detailed_spec.md)

---

## Overview

Implement basic CRUD operations for Organizations to provide multi-tenant data isolation. This includes creating organizations (Super Admin only), retrieving organization details, updating organizations, and listing organizations with appropriate permissions.

**Scope**: REQ-ORG-001, REQ-ORG-002, REQ-ORG-003, REQ-ORG-004

**Out of Scope** (for later): REQ-ORG-005 (data isolation enforcement across all entities), REQ-ORG-006 (cross-organization access prevention) - these will be implemented incrementally as we add Projects and Tickets

---

## Task 1: Organization domain models and validation
**Status**: ⏳ Pending
**Implements**: Foundation for REQ-ORG-001, REQ-ORG-002, REQ-ORG-003, REQ-ORG-004

### Description
Create domain models for Organizations with validation rules.

### Requirements from Spec
- Organization data structure (name, description, is_active, timestamps)
- Validation: name required, max 255 chars, unique constraint
- OrganizationCreateCommand and OrganizationUpdateCommand

### Implementation Checklist
- [ ] Create `Organization` domain model (id, name, description, is_active, created_at, updated_at)
- [ ] Create `OrganizationData` model for input validation (name, description)
- [ ] Create `OrganizationCreateCommand` model
- [ ] Create `OrganizationUpdateCommand` model
- [ ] Add validation rules (name length, required fields)
- [ ] Write domain validation tests in `tests/domain/test_organization_models.py`

---

## Task 2: Organization repository layer
**Status**: ⏳ Pending
**Implements**: Foundation for REQ-ORG-001, REQ-ORG-002, REQ-ORG-003, REQ-ORG-004
**Dependencies**: Task 1

### Description
Implement repository methods for Organization CRUD operations in the DAL layer.

### Requirements from Spec
- Create organization with unique name validation
- Retrieve organization by ID
- Update organization (name, description, is_active)
- List all organizations
- Proper ORM-to-domain conversion

### Implementation Checklist
- [ ] Create `OrganizationORM` model in `orm_data_models.py`
- [ ] Add organization table with unique name constraint
- [ ] Create converter `orm_organization_to_domain_organization()`
- [ ] Implement `repo.organizations.create()` method
- [ ] Implement `repo.organizations.get_by_id()` method
- [ ] Implement `repo.organizations.get_all()` method
- [ ] Implement `repo.organizations.update()` method
- [ ] Implement `repo.organizations.delete()` method (for cleanup, not exposed in V1 API)
- [ ] Handle unique constraint violations (duplicate names)
- [ ] Write repository tests in `tests/dal/test_organization_repository.py`

---

## Task 3: Organization API endpoints
**Status**: ⏳ Pending
**Implements**: REQ-ORG-001, REQ-ORG-002, REQ-ORG-003, REQ-ORG-004
**Dependencies**: Task 1, Task 2

### Description
Create REST API endpoints for Organizations with role-based permissions.

### Requirements from Spec
- POST /api/organizations (Super Admin only) - Create organization
- GET /api/organizations/{id} (Super Admin: any org, Others: own org only) - Get organization
- GET /api/organizations (Super Admin: all orgs, Others: own org only) - List organizations
- PUT /api/organizations/{id} (Super Admin only) - Update organization
- Enforce permissions: Only Super Admin can create/update
- Regular users can only view their own organization
- Proper error responses (403, 404, 400)

### Implementation Checklist
- [ ] Create `routers/organization_api.py` with router setup
- [ ] Implement POST /api/organizations (require Super Admin role)
- [ ] Implement GET /api/organizations/{id} (permission-filtered)
- [ ] Implement GET /api/organizations (permission-filtered list)
- [ ] Implement PUT /api/organizations/{id} (require Super Admin role)
- [ ] Add permission checks using auth dependencies
- [ ] Return 403 for non-Super Admin creating/updating organizations
- [ ] Return 403 for users accessing other organizations' data
- [ ] Return 404 for non-existent organizations
- [ ] Return 400 for duplicate organization names
- [ ] Include router in `app.py`
- [ ] Write comprehensive API tests in `tests/api/test_organization_api.py`

---

## Task 4: Organization integration and edge cases
**Status**: ⏳ Pending
**Implements**: Edge cases for REQ-ORG-001, REQ-ORG-002, REQ-ORG-003, REQ-ORG-004
**Dependencies**: Task 3

### Description
Test edge cases and integration scenarios for Organizations.

### Requirements from Spec
- Validate edge cases (special characters, unicode, max/min lengths)
- Test duplicate name handling
- Test Super Admin vs regular user permissions
- Test inactive organizations behavior
- Ensure complete workflow coverage

### Implementation Checklist
- [ ] Test creating organization with max length name (255 chars)
- [ ] Test creating organization with special characters
- [ ] Test creating organization with unicode characters
- [ ] Test duplicate organization name returns 400
- [ ] Test Super Admin can create/update/view all organizations
- [ ] Test Admin can only view their own organization
- [ ] Test other roles (Project Manager, Write, Read) can only view their own organization
- [ ] Test updating organization to duplicate name fails
- [ ] Test deactivating organization (is_active = false)
- [ ] Test optional vs required fields
- [ ] Complete workflow tests (create → retrieve → update → list)
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
- [ ] REQ-ORG-001 marked ✅ in `organizations_detailed_spec.md`
- [ ] REQ-ORG-002 marked ✅ in `organizations_detailed_spec.md`
- [ ] REQ-ORG-003 marked ✅ in `organizations_detailed_spec.md`
- [ ] REQ-ORG-004 marked ✅ in `organizations_detailed_spec.md`
- [ ] Feature status updated in `main_spec.md` to 🟡 4/6 (67%)

### Archival
- [ ] Archive this file to `archive/2025-01-23_organizations_crud.md`
- [ ] Clear `current_task_list.md` or create new task list for next feature

---

## Notes

**Data Isolation**: REQ-ORG-005 and REQ-ORG-006 (data isolation between organizations) will be implemented incrementally:
- Basic checks in this task (users can only view their own org)
- Full enforcement when implementing Projects (organization_id filtering)
- Complete isolation when implementing Tickets (cross-entity validation)

**Delete Operation**: Repository implements delete for testing/cleanup, but it's not exposed in the V1 API (organizations are deactivated via is_active flag instead).

**Super Admin Bootstrap**: Super Admin created by bootstrap process already exists, so we can immediately test Super Admin operations.
