# Role-Based Access Control: Detailed Specification

**Status**: 🟢 9/10 requirements implemented (90%)
**Parent**: [Main Spec](../main_spec.md#feature-role-based-access-control)
**Last Updated**: 2025-01-25

## Rationale

Different users need different levels of access to system resources. The system implements role-based access control (RBAC) with five distinct roles, each with specific permissions. This ensures users can only perform actions appropriate to their role while maintaining data security and organizational boundaries.

---

## Role Definitions

The system supports five roles with hierarchical permissions:

1. **Super Admin**: System-wide access, manages organizations, cross-organization access
2. **Admin**: Full access within assigned organization, user management
3. **Project Manager**: Manage projects and tickets within organization
4. **Write Access**: Create and update tickets within organization
5. **Read Access**: View-only access within organization

---

## REQ-RBAC-001: Super Admin can manage organizations and create organization admins
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a Super Admin manages organizations and users

### Observable Behavior
Only Super Admin users can create and manage organizations. Super Admins can create users (including Admins) in any organization.

### Acceptance Criteria
- POST /api/organizations requires Super Admin role (403 otherwise)
- PUT /api/organizations/{id} requires Super Admin role (403 otherwise)
- POST /api/users with any organization_id succeeds for Super Admin
- POST /api/users with different organization_id fails for Org Admin (403)
- Super Admin can create users with Admin role in any organization
- Org Admins can only create users in their own organization

### Implementation
- `organization_api.py` create_organization (line 28): Uses `get_super_admin_user()` dependency
- `organization_api.py` update_organization (line 155): Uses `get_super_admin_user()` dependency
- `user_api.py` create_user (lines 76-80): Super Admin bypasses organization check

### Edge Cases
- Super Admin creating user without organization_id (succeeds for Super Admin users)
- Org Admin attempting cross-organization user creation (403)

---

## REQ-RBAC-002: Super Admin can access all organizations
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a Super Admin accesses organization data

### Observable Behavior
Super Admin users can view and access all organizations' data. Regular users can only access their assigned organization.

### Acceptance Criteria
- GET /api/organizations returns all organizations for Super Admin
- GET /api/organizations returns only user's organization for regular users
- GET /api/organizations/{id} succeeds for any organization_id for Super Admin
- GET /api/organizations/{id} returns 403 for other organizations for regular users
- GET /api/projects returns all projects for Super Admin
- GET /api/projects returns only user's organization's projects for regular users
- GET /api/tickets returns all tickets for Super Admin
- GET /api/tickets returns only user's organization's tickets for regular users

### Implementation
- All list endpoints check `if current_user.role == UserRole.SUPER_ADMIN` and bypass organization filtering
- Examples: `organization_api.py` (line 135), `project_api.py` (line 151), `ticket_api.py` (line 270)

### Edge Cases
- Super Admin with no organization_id (valid, can access all)
- Regular user attempting to filter by different organization (ignored, uses their org)

---

## REQ-RBAC-003: Admin role has full access within their organization
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an Admin user manages resources in their organization

### Observable Behavior
Admin users have full CRUD access to all resources within their organization but cannot access other organizations.

### Acceptance Criteria
- Admin can create projects in their organization
- Admin can update projects in their organization
- Admin can delete projects in their organization
- Admin can create users in their organization
- Admin can update users in their organization
- Admin can delete users in their organization
- Admin can create/update/delete tickets in their organization
- Admin cannot access resources in other organizations (403)

### Implementation
- Allowed roles include `UserRole.ADMIN` on all endpoints
- Organization scoping enforced (403 for cross-org access)
- Examples: `project_api.py` (lines 53, 198, 261), `user_api.py` (lines 25, 224, 309)

### Edge Cases
- Admin attempting to access another organization's resources (403)
- Admin attempting to update organization settings (403, only Super Admin)

---

## REQ-RBAC-004: Project Manager can manage projects and tickets
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a Project Manager manages projects and tickets

### Observable Behavior
Project Managers can create and update projects and tickets, but cannot delete them (only Admin can delete).

### Acceptance Criteria
- PM can create projects (POST /api/projects)
- PM can update projects (PUT /api/projects/{id})
- PM cannot delete projects (DELETE /api/projects/{id} returns 403)
- PM can create tickets (POST /api/tickets)
- PM can update tickets (PUT /api/tickets/{id})
- PM can change ticket status (PUT /api/tickets/{id}/status)
- PM can move tickets between projects (PUT /api/tickets/{id}/project)
- PM can assign tickets to users (PUT /api/tickets/{id}/assignee)
- PM cannot delete tickets (DELETE /api/tickets/{id} returns 403)

### Implementation
- `project_api.py`: PROJECT_MANAGER in allowed roles for create (line 53) and update (line 198)
- `project_api.py`: PROJECT_MANAGER NOT in allowed roles for delete (line 261)
- `ticket_api.py`: PROJECT_MANAGER in allowed roles for all operations except delete (lines 155, 333, 386, 440, 500)
- `ticket_api.py`: PROJECT_MANAGER NOT in allowed roles for delete (line 571)

### Edge Cases
- PM attempting to delete project (403)
- PM attempting to delete ticket (403)
- PM managing tickets across organizations (403 via organization scoping)

---

## REQ-RBAC-005: Write Access users can create/update tickets
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a Write Access user works with tickets

### Observable Behavior
Write Access users can create and update tickets but cannot perform management operations like moving, assigning, or deleting.

### Acceptance Criteria
- Write user can create tickets (POST /api/tickets)
- Write user can update ticket fields (PUT /api/tickets/{id})
- Write user can change ticket status (PUT /api/tickets/{id}/status)
- Write user cannot move tickets (PUT /api/tickets/{id}/project returns 403)
- Write user cannot assign tickets (PUT /api/tickets/{id}/assignee returns 403)
- Write user cannot delete tickets (DELETE /api/tickets/{id} returns 403)
- Write user cannot create projects (POST /api/projects returns 403)
- Write user cannot update projects (PUT /api/projects/{id} returns 403)

### Implementation
- `ticket_api.py`: WRITE_ACCESS in allowed roles for create (line 155), update (line 333), status change (line 386)
- `ticket_api.py`: WRITE_ACCESS NOT in allowed roles for move (line 440), assign (line 500), delete (line 571)
- `project_api.py`: WRITE_ACCESS NOT in allowed roles for any project operations (lines 53, 198, 261)

### Edge Cases
- Write user attempting project operations (403)
- Write user attempting ticket assignment (403)
- Write user updating their own assigned tickets (succeeds)

---

## REQ-RBAC-006: Read Access users can only view
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a Read Access user attempts to view or modify data

### Observable Behavior
Read Access users can view all data within their organization but cannot create, update, or delete anything.

### Acceptance Criteria
- Read user can get projects (GET /api/projects/{id})
- Read user can list projects (GET /api/projects)
- Read user can get tickets (GET /api/tickets/{id})
- Read user can list tickets (GET /api/tickets)
- Read user can get users (GET /api/users/{id})
- Read user can list users (GET /api/users)
- Read user cannot create anything (all POST endpoints return 403)
- Read user cannot update anything (all PUT endpoints return 403)
- Read user cannot delete anything (all DELETE endpoints return 403)

### Implementation
- All GET endpoints use `get_current_user()` which allows any authenticated user
- All POST/PUT/DELETE endpoints exclude READ_ACCESS from allowed roles
- Examples: `project_api.py` (lines 53, 198, 261), `ticket_api.py` (lines 155, 333, 386, 440, 500, 571)

### Edge Cases
- Read user attempting any write operation (403)
- Read user viewing data in their organization (succeeds)
- Read user attempting cross-organization viewing (403 via organization scoping)

---

## REQ-RBAC-007: Enforce permissions on all endpoints
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When any user accesses any API endpoint

### Observable Behavior
All API endpoints enforce role-based permissions. No endpoint is accessible without appropriate role.

### Acceptance Criteria
- All endpoints require authentication (401 without token)
- All endpoints check user role before allowing operation
- 23 total endpoints with permission enforcement:
  - Organizations: 4 endpoints (create, get, list, update)
  - Users: 5 endpoints (create, get, list, update, delete)
  - Projects: 5 endpoints (create, get, list, update, delete)
  - Tickets: 9 endpoints (create, get, list, update, status, move, assign, delete)
- Each endpoint either uses role-specific dependency or manual role check
- Unauthenticated requests return 401
- Authenticated but insufficient permissions return 403

### Implementation
**Pattern 1 - Dependency Injection**:
```python
super_admin: User = Depends(get_super_admin_user)  # Only Super Admin
admin: User = Depends(get_admin_user)              # Admin or Super Admin
current_user: User = Depends(get_current_user)     # Any authenticated user
```

**Pattern 2 - Manual Role Checks**:
```python
allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER}
if current_user.role not in allowed_roles:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Edge Cases
- Endpoint with no authentication (none exist - all require token)
- Endpoint with authentication but no role check (none exist - all have role enforcement)

---

## REQ-RBAC-008: Return 403 for unauthorized actions
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user attempts an action they don't have permission for

### Observable Behavior
System returns HTTP 403 Forbidden with clear error message when user lacks permission.

### Acceptance Criteria
- 403 status code for all unauthorized actions
- Error response includes "detail" field with clear message
- Error messages are consistent: "Insufficient permissions to [action]"
- Examples:
  - "Insufficient permissions to create projects"
  - "Insufficient permissions to delete tickets"
  - "Super Admin access required"
  - "Admin access required"

### Implementation
- `dependencies.py`: `InsufficientPermissionsException` used throughout (lines 95-107, 118-120, 138-140)
- All API files use consistent 403 responses
- Examples: `project_api.py` (lines 56-59, 201-204, 264-267), `ticket_api.py` (lines 158-161, 336-339)

### Edge Cases
- 401 for missing/invalid token (not 403 - authentication vs authorization)
- 404 for non-existent resource (not 403 - checked before permission)
- 403 only when authenticated user lacks permission

---

## REQ-RBAC-009: Users see only data they have permission for
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When users list or query data

### Observable Behavior
All list/query endpoints automatically filter results based on user's organization. Users cannot see data from other organizations (except Super Admin).

### Acceptance Criteria
- Organization list filtered by user's organization (except Super Admin sees all)
- Project list filtered by user's organization (except Super Admin sees all)
- Ticket list filtered by user's organization projects (except Super Admin sees all)
- User list filtered by user's organization (except Super Admin sees all)
- Attempting to access resource from another organization returns 404 (not 403 to avoid info leakage)
- Super Admin sees all data across all organizations

### Implementation
**Organizations** (`organization_api.py`, line 135):
```python
if current_user.role == UserRole.SUPER_ADMIN:
    organizations = repo.organizations.get_all()
else:
    organization = repo.organizations.get_by_id(current_user.organization_id)
    return [organization] if organization else []
```

**Projects** (`project_api.py`, line 151):
```python
if current_user.role == UserRole.SUPER_ADMIN:
    projects = repo.projects.get_all()
else:
    projects = repo.projects.get_by_organization_id(current_user.organization_id)
```

**Tickets** (`ticket_api.py`, lines 270-302):
```python
if current_user.role == UserRole.SUPER_ADMIN:
    return repo.tickets.get_by_filters(...)
else:
    user_org_projects = repo.projects.get_by_organization_id(current_user.organization_id)
    user_project_ids = {p.id for p in user_org_projects}
    # Filter tickets to only those in user's org projects
```

**Users** (`user_api.py`, line 203):
```python
if current_user.role != UserRole.SUPER_ADMIN:
    organization_id = current_user.organization_id  # Override to user's org
```

### Edge Cases
- Empty organization (returns empty list)
- Super Admin with organization_id=None (sees all)
- Regular user attempting to filter by different org (ignored, uses their org)

---

## REQ-RBAC-010: Activity logs reflect user permissions
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When users view activity logs

### Observable Behavior
Activity logs are filtered based on user permissions - users only see logs for resources they can access.

### Acceptance Criteria
- Users can only view activity logs for resources in their organization
- Super Admin can view activity logs across all organizations
- Activity log access respects same permissions as resource access
- If user cannot view resource, they cannot view its activity logs

### Implementation Status
**NOT IMPLEMENTED** - This requirement depends on the Activity Logs & Audit Trails feature, which has not been implemented yet (0/7 requirements).

**What's missing**:
- No activity log database table
- No activity log domain model
- No activity log API endpoints
- No permission-based filtering for activity logs

**Note**: This requirement will be implemented as part of the Activity Logs & Audit Trails feature.

---

## Test Coverage

### Comprehensive Permission Tests (125+ tests)

**Organization API Tests** (24 tests):
- `test_create_organization_as_super_admin` - Verifies Super Admin can create
- `test_create_organization_as_regular_user_fails` - Verifies 403 for non-Super Admin
- `test_get_other_organization_as_regular_user_fails` - Verifies 403 for cross-org access
- `test_list_organizations_as_regular_user_sees_only_own` - Verifies data scoping

**User API Tests** (33 tests):
- `test_create_user_as_super_admin` - Verifies Super Admin can create in any org
- `test_create_user_as_org_admin_in_own_org` - Verifies Admin can create in their org
- `test_create_user_as_org_admin_in_different_org_fails` - Verifies 403 for cross-org
- `test_list_users_as_org_admin_sees_only_own_org` - Verifies data scoping

**Project API Tests** (33 tests):
- `test_create_project_as_admin` - Verifies Admin can create
- `test_create_project_as_project_manager` - Verifies PM can create
- `test_create_project_as_write_user_fails` - Verifies 403 for Write user
- `test_create_project_as_read_user_fails` - Verifies 403 for Read user
- `test_delete_project_as_project_manager_fails` - Verifies PM cannot delete (403)

**Ticket API Tests** (35 tests):
- `test_create_ticket_as_admin` - Verifies Admin can create
- `test_create_ticket_as_project_manager` - Verifies PM can create
- `test_create_ticket_as_write_user` - Verifies Write user can create
- `test_create_ticket_as_read_user_fails` - Verifies 403 for Read user
- `test_move_ticket_as_write_user_fails` - Verifies Write user cannot move (403)
- `test_assign_ticket_as_write_user_fails` - Verifies Write user cannot assign (403)
- `test_delete_ticket_as_project_manager_fails` - Verifies PM cannot delete (403)

**Test Helpers**:
- Role-specific fixtures: `super_admin_token`, `org_admin_token`, `project_manager_token`, `write_user_token`, `read_user_token`
- Role-specific user creators: `create_admin_user()`, `create_project_manager()`, `create_write_user()`, `create_read_user()`

---

## Implementation Architecture

### Permission Enforcement Layers

**Layer 1: FastAPI Dependencies**
- `get_current_user()` - Validates token, fetches user, checks is_active
- `get_super_admin_user()` - Ensures user has SUPER_ADMIN role
- `get_admin_user()` - Ensures user has ADMIN or SUPER_ADMIN role

**Layer 2: Manual Role Checks**
- `allowed_roles` set defined at endpoint level
- Manual check: `if current_user.role not in allowed_roles: raise HTTPException(403)`
- Used when multiple roles are allowed

**Layer 3: Organization Scoping**
- All resources are organization-scoped (except Super Admin exemption)
- Cross-organization access returns 403 (projects/tickets) or 404 (users)
- Automatic filtering in list endpoints

### Role Hierarchy

```
Super Admin (highest)
    └── Can do everything
    └── Cross-organization access
    └── Manage organizations

Admin
    └── Full access within organization
    └── User management
    └── Can delete projects/tickets

Project Manager
    └── Create/update projects
    └── Create/update/move/assign tickets
    └── Cannot delete

Write Access
    └── Create/update tickets
    └── Cannot manage projects
    └── Cannot move/assign tickets

Read Access (lowest)
    └── View only
    └── No write operations
```

---

## Security Considerations

1. **Token-based Authentication**: All endpoints require valid JWT token
2. **Role Verification**: Role is fetched from database on each request (not from token)
3. **Organization Isolation**: Automatic filtering prevents cross-organization access
4. **Error Messages**: Consistent 403 responses don't leak sensitive information
5. **Permission Enforcement**: 100% coverage - no endpoint lacks permission checks
6. **Test Coverage**: 125+ tests verify permission boundaries

---

## Related Requirements

- ✅ REQ-AUTH-003: Validate bearer token on protected endpoints
- ✅ REQ-ORG-005: Data isolation between organizations
- ✅ REQ-ORG-006: Users cannot access other organizations' data
- ✅ REQ-USER-002: Assign user to organization with role
- ❌ REQ-ACTIVITY-006: Activity logs respect user permissions (pending Activity Logs feature)
