# User Authentication: Detailed Specification

**Status**: 🟡 5/6 requirements implemented (83%)
**Parent**: [Main Spec](../main_spec.md#feature-user-authentication)
**Last Updated**: 2025-01-25

## Rationale

Users need secure authentication to access the system. The system uses username/password authentication with bearer token-based sessions. This provides:
- Secure credential validation
- Stateless session management via JWT or similar tokens
- Token expiration for security
- Password change capability

Users receive generated passwords when created and can change them afterwards.

---

## REQ-AUTH-001: User login with username/password
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user attempts to login with their credentials

### Observable Behavior
Users can authenticate with username and password to access the system.

### Acceptance Criteria
- POST /auth/login with `{"username": "...", "password": "..."}` returns 200 on success
- Successful response includes:
  - `access_token`: Bearer token for authentication
  - `token_type`: "bearer"
  - `expires_in`: Token lifetime in seconds (e.g., 3600 for 1 hour)
  - `user_id`: ID of authenticated user
  - `organization_id`: User's organization ID
  - `role`: User's role
- Invalid credentials return 401 with error message
- Disabled/inactive users cannot login (401)
- Username is case-insensitive
- Password is case-sensitive

### Edge Cases
- Non-existent username (401, don't reveal if username exists)
- Wrong password (401, same error as non-existent username)
- Inactive user attempting login
- Empty username or password
- Very long username/password (should fail validation)
- Special characters in credentials

---

## REQ-AUTH-002: Issue bearer token on successful login
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When login succeeds, system issues a bearer token

### Observable Behavior
Valid bearer token is returned that can be used for subsequent API calls.

### Acceptance Criteria
- Token is JWT or similar standard format
- Token includes: user_id, organization_id, role, expiration
- Token can be validated without database lookup (stateless)
- Token expiration is enforced
- Multiple logins create separate tokens
- Tokens are not stored server-side (stateless)

### Edge Cases
- Concurrent logins from same user (both tokens valid)
- Token content is not modifiable (signed/encrypted)
- Token includes all necessary context to avoid database lookups

---

## REQ-AUTH-003: Validate bearer token on protected endpoints
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When a user accesses a protected endpoint

### Observable Behavior
All endpoints (except login, health check) require valid bearer token.

### Acceptance Criteria
- Request without token returns 401
- Request with invalid token returns 401
- Request with expired token returns 401
- Request with valid token succeeds
- Token is provided in Authorization header: `Bearer <token>`
- Token validation extracts user context (user_id, org_id, role)
- User context is available to all endpoints for permission checks

### Edge Cases
- Missing Authorization header
- Malformed Authorization header (not "Bearer ...")
- Invalid token format
- Expired token
- Token with invalid signature
- Token from deactivated user (should fail - need to check user status)

---

## REQ-AUTH-004: User can change their password
**Status**: 🔴 Not Implemented (ONLY REMAINING)
**Type**: Product Behavior

### Scenario
When a user wants to change their password

### Observable Behavior
Authenticated users can change their own password.

### Acceptance Criteria
- POST /auth/change-password with `{"current_password": "...", "new_password": "..."}` returns 200
- Requires valid bearer token (must be authenticated)
- Current password must be correct (401 if wrong)
- New password must meet minimum requirements:
  - Minimum 8 characters
  - At least one uppercase, lowercase, digit, special char
- After password change, user can login with new password
- After password change, old password no longer works
- Existing tokens remain valid (tokens are stateless)
- User can only change their own password
- Returns 200 with success message

### Edge Cases
- Wrong current password
- New password same as current password (should succeed)
- New password too weak (fails validation)
- Very long new password
- Special characters in password
- Admin changing another user's password (different endpoint, REQ-USER-003)

---

## REQ-AUTH-005: Token expiration and refresh
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When tokens expire or users need to refresh

### Observable Behavior
Tokens have limited lifetime and users must re-authenticate when expired.

### Acceptance Criteria
- Tokens expire after configured duration (e.g., 1 hour, 24 hours)
- Expired token returns 401 with specific error: "Token expired"
- User must re-login to get new token
- No refresh token in V1 (simple re-login required)
- Token expiration is enforced on all protected endpoints
- Clock skew tolerance is reasonable (e.g., 5 minutes)

### Edge Cases
- Token about to expire (still valid until expiration)
- Token just expired (no grace period in V1)
- System clock changes (tokens still validate correctly)
- Long-lived sessions not supported in V1 (must re-login)

---

## REQ-AUTH-006: Handle authentication errors
**Status**: ✅ Implemented
**Type**: Product Behavior

### Scenario
When authentication fails for various reasons

### Observable Behavior
Clear, secure error messages guide users without leaking security information.

### Acceptance Criteria
- Invalid credentials: 401 with "Invalid credentials" (don't specify if username or password wrong)
- Missing token: 401 with "Authentication required"
- Invalid token: 401 with "Invalid token"
- Expired token: 401 with "Token expired"
- Inactive user: 401 with "Account inactive"
- All 401 responses have consistent format:
  ```json
  {
    "detail": "Error message",
    "error_code": "INVALID_CREDENTIALS" | "TOKEN_EXPIRED" | "ACCOUNT_INACTIVE"
  }
  ```
- Error messages don't leak information about:
  - Whether username exists
  - Password requirements (until password change validation)
  - System internals

### Edge Cases
- Multiple failed login attempts (no lockout in V1, but logged)
- Timing attacks (constant-time password comparison)
- Error message consistency across all auth failures
