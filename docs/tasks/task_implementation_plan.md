# Task Implementation Plan: User data structures and password handling

**Task Status**: 🔄 In Progress
**Date**: 2025-01-20
**Implements Requirements**: Foundation for REQ-AUTH-001, REQ-USER-001

## Behaviors to Implement

### From REQ-AUTH-001: User login with username/password
**Observable Behavior**:
Users can authenticate with username and password.

**Relevant Acceptance Criteria for this task**:
- System can store user credentials securely
- Passwords are hashed, never stored in plain text
- System can verify password against stored hash
- Username is case-insensitive for login

### From REQ-USER-001: Create user with generated password
**Observable Behavior**:
Users have usernames, emails, roles, and secure passwords.

**Relevant Acceptance Criteria for this task**:
- User has required fields: username, email, full_name, organization_id, role, is_active
- System generates secure random passwords
- Password hashing uses industry-standard algorithm (bcrypt)

## Implementation Plan

### Domain Layer Changes
- [ ] Create `UserRole` enum with values: super_admin, admin, project_manager, write_access, read_access
- [ ] Create `UserData` model (Pydantic):
  - username: str (3-50 chars, alphanumeric + underscore/dash)
  - email: EmailStr (valid email)
  - full_name: str
- [ ] Create `User` model (Pydantic) extending UserData:
  - id: str (UUID)
  - organization_id: Optional[str] (None for super_admin)
  - role: UserRole
  - is_active: bool (default True)
  - created_at: datetime
  - updated_at: datetime
- [ ] Create `UserCreateCommand` model (Pydantic):
  - user_data: UserData
  - organization_id: Optional[str]
  - role: UserRole

### Repository Layer Changes
- [ ] Create `UserORM` in `dal/sqlite/orm_data_models.py`:
  - id: String (UUID primary key)
  - username: String(50, unique)
  - email: String(255)
  - full_name: String(255)
  - password_hash: String(255)
  - organization_id: String (nullable for super_admin)
  - role: String (enum values)
  - is_active: Boolean (default True)
  - created_at: DateTime
  - updated_at: DateTime
- [ ] Create converter functions in `dal/sqlite/converters.py`:
  - `orm_user_to_domain_user(orm_user: UserORM) -> User`
  - (Note: password_hash is NOT included in domain User model)

### Utility Layer
- [ ] Create `utils/password.py` with functions:
  - `hash_password(plain_password: str) -> str`: Hash password with bcrypt
  - `verify_password(plain_password: str, password_hash: str) -> bool`: Verify password
  - `generate_password() -> str`: Generate secure random password (12+ chars, mixed case, digits, special chars)

### Database Changes
- [ ] Update `dal/sqlite/database.py` to create users table
- [ ] Add users table to create_tables() method

## Test Planning

### 1. Domain Model Validation Tests
**File**: `tests/domain/test_user_models.py`

**Tests**:
- `test_user_data_with_valid_fields_validates`
  - Verifies: UserData accepts valid username, email, full_name
  - Assertions: Model creation succeeds, fields are correct

- `test_user_data_with_invalid_username_fails`
  - Verifies: Username validation (length, characters)
  - Assertions: ValidationError for empty, too short, too long, invalid chars

- `test_user_data_with_invalid_email_fails`
  - Verifies: Email validation
  - Assertions: ValidationError for malformed emails

- `test_user_model_includes_all_fields`
  - Verifies: User model has all required fields
  - Assertions: All fields present (id, org_id, role, is_active, timestamps)

- `test_user_role_enum_has_all_roles`
  - Verifies: UserRole enum has all 5 roles
  - Assertions: Enum has super_admin, admin, project_manager, write_access, read_access

### 2. Password Utility Tests
**File**: `tests/utils/test_password.py`

**Tests**:
- `test_hash_password_creates_valid_bcrypt_hash`
  - Verifies: Password is hashed with bcrypt
  - Steps: Hash a password, check result starts with bcrypt prefix
  - Assertions: Hash is string, has correct format

- `test_hash_password_different_each_time`
  - Verifies: Same password creates different hashes (salt)
  - Steps: Hash same password twice
  - Assertions: Two hashes are different

- `test_verify_password_with_correct_password_succeeds`
  - Verifies: Correct password verification
  - Steps: Hash password, verify with same password
  - Assertions: verify_password returns True

- `test_verify_password_with_wrong_password_fails`
  - Verifies: Wrong password verification fails
  - Steps: Hash password, verify with different password
  - Assertions: verify_password returns False

- `test_generate_password_creates_secure_password`
  - Verifies: Generated password meets requirements
  - Steps: Generate password
  - Assertions: Length >= 12, has uppercase, lowercase, digit, special char

- `test_generate_password_creates_different_passwords`
  - Verifies: Each generated password is unique
  - Steps: Generate 10 passwords
  - Assertions: All passwords are different

### 3. Repository Layer Tests
**File**: `tests/dal/test_user_repository.py`

**Tests**:
- `test_create_user_stores_password_hash`
  - Verifies: User is created with hashed password
  - Steps: Create UserORM with password_hash, save to DB, retrieve
  - Assertions: User exists in DB, password_hash is stored (not plain password)

- `test_orm_to_domain_user_excludes_password_hash`
  - Verifies: Domain User doesn't include password_hash
  - Steps: Create UserORM, convert to domain User
  - Assertions: Domain User has no password_hash attribute

- `test_user_username_is_unique`
  - Verifies: Cannot create duplicate username
  - Steps: Create user, attempt to create another with same username
  - Assertions: Second creation fails (DB constraint)

## Existing Tests to Update

None - this is foundation work with no existing user functionality.

## Dependencies

**Requires**: None (this is the first task)

**Blocks**: Task 2 (Token generation), Task 3 (Login endpoint)

## Notes

- Password utilities use bcrypt (industry standard for password hashing)
- Domain User model deliberately excludes password_hash (security best practice)
- organization_id is Optional to support Super Admin (no org assignment)
- No repository methods yet - those come in Task 3 when we need to fetch users
