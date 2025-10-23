# Task 3 Implementation Plan: Login and Authentication

**Task**: Login and authentication
**Implements**: REQ-AUTH-001, REQ-AUTH-002, REQ-AUTH-003, REQ-AUTH-006
**Created**: 2025-01-23

## Requirements Analysis

### From REQ-AUTH-001: User login with username/password
- POST /auth/login endpoint
- Request: `{"username": "...", "password": "..."}`
- Response: `{access_token, token_type, expires_in, user_id, organization_id, role}`
- Username is case-insensitive, password is case-sensitive
- Inactive users cannot login (401)
- Invalid credentials return 401

### From REQ-AUTH-002: Issue bearer token
- Generate JWT token on successful login
- Token includes user_id, organization_id (role fetched from DB)
- Multiple logins create separate tokens

### From REQ-AUTH-003: Validate bearer token on protected endpoints
- Token in Authorization header: `Bearer <token>`
- Extract user context from token
- Fetch user from DB to get current role and check is_active
- User context available to all endpoints

### From REQ-AUTH-006: Handle authentication errors
- Consistent error format with detail and error_code
- Don't leak username existence
- Constant-time password comparison (bcrypt does this automatically)

## Behaviors to Implement

### 1. Login Endpoint (POST /auth/login)
**Input**: LoginRequest(username, password)
**Output**: LoginResponse OR 401 error
**Behavior**:
- Look up user by username (case-insensitive)
- If user not found → 401 "Invalid credentials"
- If user found but inactive → 401 "Account inactive"
- Verify password using bcrypt
- If password wrong → 401 "Invalid credentials"
- If success: generate token, return with user info

### 2. Get Current User (dependency for protected endpoints)
**Input**: Authorization header with Bearer token
**Output**: User domain model OR raises 401
**Behavior**:
- Extract token from Authorization header
- Decode and validate token (signature, expiration)
- Fetch user from DB by user_id
- Check if user exists and is_active
- Return user with current role

### 3. Error Handling
**Consistent format**:
```json
{
  "detail": "Human readable message",
  "error_code": "INVALID_CREDENTIALS" | "TOKEN_EXPIRED" | "ACCOUNT_INACTIVE" | "AUTHENTICATION_REQUIRED"
}
```

## Implementation Plan

### 1. Domain Models (`project_management_crud_example/domain_models.py`)
```python
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: str
    organization_id: Optional[str]
    role: UserRole
```

### 2. Auth Router (`project_management_crud_example/routers/auth_api.py`)
```python
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, repo: Repository = Depends(get_repository)):
    # Implementation
```

### 3. Authentication Dependency (`project_management_crud_example/dependencies.py`)
```python
async def get_current_user(
    authorization: str = Header(None),
    repo: Repository = Depends(get_repository)
) -> User:
    """Extract and validate user from Bearer token."""
    # Validate Authorization header format
    # Decode token
    # Fetch user from DB
    # Check is_active
    # Return user
```

### 4. Custom HTTP Exceptions
Create structured exception classes for auth errors with proper error_code.

## Test Plan

### API Tests (`tests/api/test_auth_api.py`)

**Login Tests (12 tests)**:
1. `test_login_with_valid_credentials_succeeds` - 200 with token
2. `test_login_response_includes_all_fields` - access_token, token_type, expires_in, user_id, org_id, role
3. `test_login_with_wrong_password_fails` - 401 INVALID_CREDENTIALS
4. `test_login_with_nonexistent_user_fails` - 401 INVALID_CREDENTIALS (same message)
5. `test_login_with_inactive_user_fails` - 401 ACCOUNT_INACTIVE
6. `test_login_username_is_case_insensitive` - "TestUser" == "testuser"
7. `test_login_password_is_case_sensitive` - "Password" != "password"
8. `test_login_with_empty_username_fails` - 422 validation error
9. `test_login_with_empty_password_fails` - 422 validation error
10. `test_login_generates_valid_token` - Token can be decoded
11. `test_multiple_logins_create_different_tokens` - Concurrent logins work
12. `test_login_for_super_admin_without_org` - Super admin can login

**Protected Endpoint Tests (8 tests)**:
1. `test_request_without_token_returns_401` - AUTHENTICATION_REQUIRED
2. `test_request_with_valid_token_succeeds` - Gets current user
3. `test_request_with_expired_token_fails` - 401 TOKEN_EXPIRED
4. `test_request_with_invalid_token_fails` - 401 invalid token
5. `test_request_with_malformed_auth_header_fails` - 401
6. `test_request_with_deactivated_user_token_fails` - User deactivated after token issued
7. `test_token_validation_fetches_current_role` - Role changes reflected immediately
8. `test_get_current_user_returns_full_user_model` - All user fields present

**Total: 20 tests**

## Implementation Order
1. Create domain models (LoginRequest, LoginResponse)
2. Create custom HTTP exception classes
3. Implement get_repository dependency
4. Implement get_current_user dependency
5. Create auth router with login endpoint
6. Register auth router in app
7. Write all tests
8. Run validations until zero errors

## Notes
- Username lookup must be case-insensitive (use SQL LOWER() or Python .lower())
- Password verification uses bcrypt (already constant-time)
- Error messages must not reveal username existence
- Token validation checks user is_active on every request
- Role is fetched fresh from DB on every request (not from token)
