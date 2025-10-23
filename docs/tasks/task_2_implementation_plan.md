# Task 2 Implementation Plan: Token Generation and Validation

**Task**: Token generation and validation
**Implements**: REQ-AUTH-002, REQ-AUTH-005
**Created**: 2025-01-23

## Requirements Analysis

### From REQ-AUTH-002: Issue bearer token on successful login
- Token is JWT format
- Token includes: user_id, organization_id, role, expiration
- Token can be validated without database lookup (stateless)
- Token expiration is enforced
- Tokens are not stored server-side (stateless)

### From REQ-AUTH-005: Token expiration and refresh
- Tokens expire after configured duration
- Expired token returns 401 with "Token expired"
- Clock skew tolerance (5 minutes)

## Behaviors to Implement

### 1. Generate JWT Token
**Input**: user_id, organization_id
**Output**: JWT token string
**Behavior**:
- Creates signed JWT with claims: user_id, organization_id, exp, iat
- Uses secret key for signing
- Sets expiration based on configurable duration
- **Role is NOT stored in token** - fetched from DB on each request for immediate permission changes

### 2. Validate JWT Token
**Input**: token string
**Output**: decoded claims (user_id, organization_id) OR raises exception
**Behavior**:
- Verifies signature
- Checks expiration (with clock skew tolerance)
- Returns claims if valid
- Raises specific exceptions for different error cases
- **Role must be fetched separately** from database using user_id

### 3. Token Configuration
- Secret key (from environment variable)
- Token lifetime (configurable, default 1 hour)
- Clock skew tolerance (5 minutes)
- Algorithm (HS256)

## Implementation Plan

### 1. Configuration Module (`project_management_crud_example/config.py`)
```python
class Settings(BaseSettings):
    JWT_SECRET_KEY: str  # Required, from env
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600  # 1 hour default
    JWT_CLOCK_SKEW_SECONDS: int = 300  # 5 minutes
```

### 2. JWT Utilities (`project_management_crud_example/utils/jwt.py`)
```python
def create_access_token(
    user_id: str,
    organization_id: Optional[str],
    role: UserRole,
) -> str:
    """Generate JWT token with user claims."""

def decode_access_token(token: str) -> dict:
    """Validate and decode JWT token.

    Raises:
        TokenExpiredError: Token has expired
        InvalidTokenError: Token is invalid/malformed
    """

class TokenClaims(BaseModel):
    """Structured token claims."""
    user_id: str
    organization_id: Optional[str]
    role: UserRole
    exp: int
    iat: int
```

### 3. Custom Exceptions (`project_management_crud_example/exceptions.py`)
```python
class TokenExpiredError(Exception):
    """Token has expired."""

class InvalidTokenError(Exception):
    """Token is invalid or malformed."""
```

## Test Plan

### Utility Tests (`tests/utils/test_jwt.py`)

**Token Generation Tests (6 tests)**:
1. `test_create_token_includes_all_claims` - Verify all claims present
2. `test_create_token_for_regular_user` - User with organization
3. `test_create_token_for_super_admin` - Super admin without organization
4. `test_create_token_sets_expiration` - Expiration set correctly
5. `test_create_token_is_signed` - Token is properly signed
6. `test_multiple_tokens_are_different` - Each token unique (different iat)

**Token Validation Tests (8 tests)**:
1. `test_decode_valid_token_succeeds` - Valid token decoded successfully
2. `test_decode_token_returns_correct_claims` - All claims extracted correctly
3. `test_decode_expired_token_raises_error` - Expired token raises TokenExpiredError
4. `test_decode_invalid_signature_raises_error` - Wrong signature raises InvalidTokenError
5. `test_decode_malformed_token_raises_error` - Malformed token raises InvalidTokenError
6. `test_decode_token_with_clock_skew` - Recently expired within skew tolerance
7. `test_decode_token_role_conversion` - Role string converted to UserRole enum
8. `test_decode_token_with_null_organization` - Super admin null org_id handled

**Configuration Tests (2 tests)**:
1. `test_settings_loads_from_env` - JWT_SECRET_KEY from environment
2. `test_settings_has_defaults` - Default values for algorithm, expiration, skew

**Total: 16 tests**

## Dependencies
- PyJWT library for JWT operations
- python-dotenv for environment configuration (if not already included)
- Pydantic settings for configuration

## Implementation Order
1. Install PyJWT dependency
2. Create config module with Settings
3. Create custom exceptions
4. Implement jwt.py utilities
5. Write all tests
6. Run validations until zero errors

## Notes
- Secret key MUST be loaded from environment (security)
- Token payload should be minimal (performance)
- No database lookups during validation (stateless)
- Clock skew prevents issues with slight time differences
