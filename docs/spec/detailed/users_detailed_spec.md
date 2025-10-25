# User Management: Detailed Specification

**Status**: 🟢 8/8 requirements implemented (100%)
**Parent**: [Main Spec](../main_spec.md#feature-user-management)
**Last Updated**: 2025-01-25

## Rationale

Users need to be created and managed within the system. Two types of user creation:
1. **Super Admin** creating organization admins
2. **Organization Admins** creating users within their organization

New users receive a generated password that is returned ONCE upon creation. Users must save this password as it cannot be retrieved later. Users can change their password after first login.

---

## REQ-USER-001: Create user with generated password
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an authorized user (Super Admin or Org Admin) creates a new user

### Observable Behavior
Authorized users can create new users with auto-generated secure passwords.

### Acceptance Criteria
- POST /users with user data returns 201
- Request body includes:
  - `username`: Unique username (3-50 chars, alphanumeric + underscore/dash)
  - `email`: Valid email address
  - `full_name`: User's full name
  - `organization_id`: Organization to assign user to
  - `role`: User's role (admin, project_manager, write_access, read_access)
- Super Admin can create users in any organization
- Org Admin can only create users in their own organization
- System generates secure random password (minimum 12 chars, mixed case, digits, special chars)
- Response includes created user AND generated password:
  ```json
  {
    "user": {
      "id": "...",
      "username": "...",
      "email": "...",
      "full_name": "...",
      "organization_id": "...",
      "role": "...",
      "is_active": true,
      "created_at": "...",
      "updated_at": "..."
    },
    "generated_password": "Abc123!@#XyzQ1w2E3"
  }
  ```
- **Password is ONLY returned in create response** - cannot be retrieved later
- Username must be unique across entire system
- Email must be unique within organization
- After creation, user can login with username and generated password
- New user appears in GET /users list

### Edge Cases
- Duplicate username (400)
- Duplicate email within org (400)
- Invalid email format (400)
- Invalid username format (400)
- Non-existent organization_id (400)
- Org Admin creating user in different org (403)
- Invalid role value (400)
- Very long names or emails
- Special characters in username (only alphanumeric, underscore, dash allowed)

---

## REQ-USER-002: Assign user to organization with role
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When creating or updating a user, they are assigned to an organization with a specific role

### Observable Behavior
Users belong to exactly one organization and have one role within that organization.

### Acceptance Criteria
- User creation requires organization_id and role
- Valid roles: `admin`, `project_manager`, `write_access`, `read_access`
- Super Admin role is NOT assignable via this endpoint (Super Admin is system-level)
- User can only access data within their assigned organization
- Role determines user's permissions (see RBAC spec)
- Organization assignment cannot be changed after creation (delete and recreate instead)
- Role can be changed via update endpoint
- GET /users/{id} returns user with organization_id and role

### Edge Cases
- Attempting to assign non-existent organization
- Attempting to assign "super_admin" role (should fail - Super Admin is system-level)
- User with no organization (should not be possible)
- Changing organization_id via update (should fail or be ignored)

---

## REQ-USER-003: Update user details
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an authorized user updates user details

### Observable Behavior
Authorized users can update user information.

### Acceptance Criteria
- PUT /users/{id} with updated data returns 200
- Super Admin can update any user
- Org Admin can update users in their organization only
- Regular users cannot update other users (403)
- Updatable fields:
  - `email`: New email (must be unique in org)
  - `full_name`: New full name
  - `role`: New role (Super Admin / Org Admin only)
  - `is_active`: Active status (Super Admin / Org Admin only)
- Non-updatable fields:
  - `username`: Cannot be changed
  - `organization_id`: Cannot be changed
  - `password`: Use /auth/change-password instead
- After update, GET returns updated data
- updated_at timestamp is updated
- Changing role takes effect immediately (user's permissions change)
- User can update their own non-protected fields (email, full_name)

### Edge Cases
- Updating to duplicate email in org
- Updating protected fields as regular user (should be ignored or 403)
- Deactivating user via is_active (user cannot login)
- Changing role to invalid value
- Admin updating user from different org (403)

---

## REQ-USER-004: Deactivate/activate user
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an authorized user deactivates or reactivates a user account

### Observable Behavior
Users can be deactivated (soft delete) and reactivated.

### Acceptance Criteria
- PUT /users/{id} with `{"is_active": false}` deactivates user
- PUT /users/{id} with `{"is_active": true}` reactivates user
- Only Super Admin or Org Admin can change is_active status
- Deactivated users cannot login (401)
- Deactivated users' existing tokens remain valid until expiration (stateless tokens)
- Deactivated users appear in GET /users list but with is_active: false
- Can filter users by is_active status
- Deactivated users' data (created tickets, comments) remains visible
- Reactivating user allows them to login again

### Edge Cases
- Deactivating user who is currently logged in (their token works until expiry)
- Deactivating self (admin deactivating themselves - should succeed but be careful)
- Filtering for active vs inactive users
- Deactivated user attempting to login

---

## REQ-USER-005: Delete user
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When an authorized user permanently deletes a user

### Observable Behavior
Users can be permanently deleted from the system.

### Acceptance Criteria
- DELETE /users/{id} returns 204 (no content)
- Only Super Admin can delete users (hard delete)
- Org Admin can only deactivate, not delete
- After deletion, GET /users/{id} returns 404
- Deleted user does not appear in GET /users list
- Deleted user cannot login
- Username becomes available for reuse
- **Data references**:
  - Option 1: Cascade delete user's data (tickets, comments become "Deleted User")
  - Option 2: Prevent deletion if user has created data (400 error)
  - **V1 Decision**: Prevent deletion if user has created data (safer)
- After deletion, audit logs remain with user ID but user details are gone

### Edge Cases
- Deleting user with created tickets/comments (should fail in V1)
- Deleting already deleted user (404)
- Deleting self as Super Admin (should succeed but be careful)
- Username reuse after deletion

---

## REQ-USER-006: List users (with filtering)
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user requests list of users

### Observable Behavior
Users can list users based on their permissions and apply filters.

### Acceptance Criteria
- GET /users returns 200 with array of users
- Super Admin sees all users across all organizations
- Org Admin sees only users in their organization
- Regular users see only users in their organization (for assignment purposes)
- Can filter by:
  - `organization_id`: Filter by organization (Super Admin only)
  - `role`: Filter by specific role
  - `is_active`: Filter by active status
- Results are paginated if large number of users
- Each user in list has same structure as individual GET (no password)
- Default: active users only

### Edge Cases
- Empty result (no users)
- Filtering by multiple criteria
- Regular user trying to filter by organization_id (ignored or 403)
- Very large user lists (pagination)
- Including inactive users in results

---

## REQ-USER-007: Retrieve user details
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user retrieves details of a specific user

### Observable Behavior
Users can retrieve user details based on permissions.

### Acceptance Criteria
- GET /users/{id} returns 200 with user data
- Super Admin can retrieve any user
- Org Admin can retrieve users in their organization
- Regular users can retrieve users in their organization
- Users cannot retrieve users from other organizations (404, not 403)
- Response includes all user fields EXCEPT password:
  - id, username, email, full_name, organization_id, role, is_active, created_at, updated_at
- Non-existent user returns 404

### Edge Cases
- Accessing user from different organization (404)
- Accessing inactive user (still returns 200 with is_active: false)
- Accessing deleted user (404)

---

## REQ-USER-008: Handle user not found errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When operations reference non-existent users

### Observable Behavior
Clear error handling for missing users without leaking cross-organization information.

### Acceptance Criteria
- GET /users/{non-existent-id} returns 404
- PUT /users/{non-existent-id} returns 404
- DELETE /users/{non-existent-id} returns 404
- Accessing user from different org returns 404 (not 403, to avoid leaking existence)
- Error response format:
  ```json
  {
    "detail": "User not found",
    "error_code": "USER_NOT_FOUND"
  }
  ```
- Error messages don't reveal:
  - Whether user exists in different organization
  - Whether username is taken
  - Organization boundaries

### Edge Cases
- Invalid user ID format
- User from different organization (appears as not found)
- Deleted user (not found)
- Deactivated user (still found, but is_active: false)
