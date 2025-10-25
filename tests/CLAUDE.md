# Testing Implementation Guidelines

This file provides guidance to Claude Code (claude.ai/code) when working on tests in this repository.

## **How to test each task**
After implementing a task, you MUST implement tests for it.
- Plan tests for the behavior in detail, follow all testing guidelines below.
- Implement the tests for this task.
- Consider if any tests for previous task need to be updated due to changes in the code, for example if existing behaviors need to support new features.
- Follow the Testing & Validations Strategy for running validations and fixing issues.

## **Testing guidelines**
A test should almost always test a single fact about the behavior of the code. test_after_put_get_returns_the_object is a good example.

Cover ALL behaviors of a feature as much as possible.

Test scope: Test behavior == cohesive whole == complete story
for example, in order to test put(), you also need to test get().
The "truth" of how some component or full software is its external observable behavior. Tests should verify using that behavior is much as possible.
It's ok to test a small part of something larger - as long as that part is a "complete stroy" in itself.
Test behaviors instead of implementations (again, an implementation detail that is in itself a cohesive whole is fine to test).
If you created a test that uses implementation details such is private members - ask yourself if you can write the test
to verify the same behavior only using external API. If yes - re-write the test.

Tests must be isolated so they never interfere with each other.

Tests must use clear language: decisive, specific and explicit.

Avoid using mocks. Simulators for quick tests are fine (for example, it's ok to test using in-memory sqlite some of the time instead of disk based for performance).

Test a variety of inputs, including variations on input data, including edge cases.

Test file names should be significant, specific and descriptive of content.
GOOD: test_basic_put_and_get.py
BAD: test_task_03_basic_put_and_get.py
BAD: test_cache.py

## Test Coverage Requirements

**Every feature implementation MUST include ALL applicable test layers:**

### **1. API Tests - ALWAYS REQUIRED ⭐⭐⭐**

**Why Critical**: Test externally observable behavior through HTTP endpoints

**Location**: `tests/api/test_*_api.py`

**Required Coverage**:
- ✅ **Happy path scenarios**: Valid requests, correct responses, proper HTTP status codes
- ✅ **Error handling**: 422 validation, 404 not found, 400 business logic violations
- ✅ **Complete workflows**: Multi-step user scenarios, data persistence verification

### **2. Repository Tests - ALWAYS REQUIRED ⭐⭐**

**Why Required**: Repository layer is a cohesive architectural layer that must work independently

**Location**: `tests/dal/test_*_repository.py`

**Required Coverage**:
- ✅ **CRUD operations**: create, read, update, delete methods
- ✅ **Data persistence**: Verify data survives round-trips
- ✅ **Error handling**: Not found, edge cases
- ✅ **Independent testing**: Test without HTTP layer

**Important**: Repository tests verify the data access layer works correctly on its own.

#### **Repository Testing Pattern - CRITICAL**

**❌ DO NOT test ORM models directly**
- Direct ORM tests are brittle and low-value
- They only verify that ORM declarations exist
- They expose implementation details

**✅ ALWAYS test through Repository methods**
- Use repository methods to create, retrieve, update, delete
- Use domain models and commands (not ORM models)
- Verify behavior through repository interface
- This provides strong correctness guarantees without brittleness

**Repository Architecture**:
- **Single `Repository` class** for all data access operations
- Use nested classes for organization: `repo.users.create()`, `repo.organizations.get_by_id()`
- Queries can span multiple entities naturally (e.g., get user with organization)
- The `StubEntityRepository` is scaffolding/example code only

**Pattern to Follow**:
```python
class TestUserOperations:
    """Test user operations through Repository interface."""

    def test_create_user(self, test_repo: Repository) -> None:
        """Test creating a user through repository."""
        # Create using repository command
        user_data = UserData(username="testuser", email="test@example.com", full_name="Test")
        command = UserCreateCommand(user_data=user_data, organization_id="org-123", role=UserRole.ADMIN)

        # Create through repository
        user = test_repo.users.create(command)

        # Verify domain model properties
        assert user.username == "testuser"
        assert user.id is not None

    def test_get_user_by_id(self, test_repo: Repository) -> None:
        """Test retrieving user through repository."""
        # Create through repository
        user_data = UserData(username="testuser", email="test@example.com", full_name="Test")
        command = UserCreateCommand(user_data=user_data, organization_id="org-123", role=UserRole.ADMIN)
        created_user = test_repo.users.create(command)

        # Retrieve through repository
        retrieved_user = test_repo.users.get_by_id(created_user.id)

        # Verify through domain model
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
```

**Key Principles**:
1. ✅ Use repository methods exclusively (no `session.query()`, no ORM access)
2. ✅ Use domain models and commands (UserData, UserCreateCommand, User)
3. ✅ Verify domain model properties (username, id, email)
4. ❌ Never access ORM models (UserORM) in tests
5. ❌ Never use test_session directly for entity creation/verification
6. ✅ Test complete workflows (create → retrieve → verify)
7. ✅ Single Repository handles all entities - queries can span multiple tables naturally

**CRITICAL ARCHITECTURAL RULE**:
- ❌ Repository methods MUST NEVER return ORM models (UserORM, etc.) to callers
- ✅ Repository methods MUST ALWAYS return domain models only
- ✅ If additional data is needed (e.g., password_hash for auth), create a specific domain model
- **Why**: Exposing ORM models breaks layering and can cause serious issues (lazy loading, session lifecycle, tight coupling)

### **3. Utility/Logic Tests - IF APPLICABLE**

**Location**: `tests/utils/` or appropriate location

**Coverage**: Helper functions, converters, business logic utilities

**Converter Tests**:
- ORM-to-domain converters should be tested in `tests/dal/test_converters.py`
- Test that converters properly transform ORM models to domain models
- Test edge cases like null values, special fields exclusions (e.g., password_hash)

### **4. Domain Validation Tests - IF APPLICABLE**

**Location**: `tests/domain/` or appropriate location

**Coverage**: Pydantic model validation, command objects, business rules

## Testing Implementation Rules

### **MANDATORY Implementation Order**
1. **First**: Write API endpoint tests that define expected behavior
2. **Second**: Implement the feature to make tests pass
3. **Third**: Add supporting DAL/unit tests as needed

### **Test Quality Requirements**

#### **Always Import PyTest Fixtures Explicitly**

**MANDATORY**: All tests must explicitly import fixtures from conftest, even though pytest auto-discovers them.

```python
# ✅ CORRECT: Explicit imports at top of test file
from fastapi.testclient import TestClient

from tests.conftest import client  # noqa: F401

class TestMyAPI:
    def test_something(self, client: TestClient) -> None:
        # ... test code
```

```python
# ❌ WRONG: Relying on auto-discovery
# Missing: from tests.conftest import client

class TestMyAPI:
    def test_something(self, client: TestClient) -> None:
        # ... test code
```

**Why**: Makes dependencies explicit, improves code clarity, prevents confusion.

#### **Test Naming Convention**
- **Pattern**: `test_[action]_[entity]_[scenario]` or `test_[scenario_description]`
- **Good**: `test_create_stub_entity`, `test_delete_stub_entity_not_found`
- **Bad**: `test_entity` (not specific enough)

#### **Test Language & Structure**
- **Decisive, explicit, specific** (not generic)
- **Test one fact** about behavior per test
- **Independent and isolated** tests
- Use **Arrange-Act-Assert** pattern

```python
def test_create_stub_entity_with_valid_data_succeeds(self, client: TestClient) -> None:
    """Test creating stub entity with valid data returns 201."""
    # Arrange
    stub_entity_data = {"name": "Test Entity", "description": "Test"}

    # Act
    response = client.post("/stub_entities", json=stub_entity_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Entity"
```

#### **Error Testing Requirements**
- **Every endpoint must test error conditions**
- **Validate proper HTTP status codes**
- **Verify error message content and format**

```python
def test_get_stub_entity_by_non_existent_id_is_not_found(self, client: TestClient) -> None:
    """Test getting a non-existent stub entity returns 404."""
    response = client.get("/stub_entities/non-existent-id")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Stub entity not found"
```

### **API Test Helper Functions - CRITICAL**

**ALWAYS use role-specific helper functions** instead of generic create_test_user with explicit role parameters.

#### **✅ CORRECT: Use Role-Specific Helpers**

```python
from tests.helpers import create_admin_user, create_project_manager, create_write_user, create_read_user

# Create admin user - expressive defaults make intent clear
user_id, password = create_admin_user(client, super_admin_token, org_id)

# Create project manager - defaults to username="projectmanager", email="pm@example.com"
pm_id, pm_password = create_project_manager(client, super_admin_token, org_id)

# Override username only when needed for test-specific reasons
user_id, password = create_write_user(client, super_admin_token, org_id, username="writer2")
```

#### **❌ WRONG: Generic Helper with Explicit Role**

```python
# DON'T DO THIS - verbose and requires manual parameter passing
user_id, password = create_test_user(
    client,
    super_admin_token,
    org_id,
    username="admin",
    email="admin@example.com",
    full_name="Admin User",
    role=UserRole.ADMIN,  # Role should be implicit in helper name
)
```

#### **Why Use Role-Specific Helpers?**

1. **Self-documenting**: `create_admin_user()` immediately communicates intent
2. **Expressive defaults**: Email "admin@example.com" clearly indicates admin user
3. **Less boilerplate**: Only override parameters when test requires specific values
4. **Consistency**: All tests use same defaults, making test data predictable

#### **Available Role-Specific Helpers**

Located in `tests/helpers.py`:

- `create_admin_user()` - username="admin", email="admin@example.com"
- `create_project_manager()` - username="projectmanager", email="pm@example.com"
- `create_write_user()` - username="writer", email="writer@example.com"
- `create_read_user()` - username="reader", email="reader@example.com"

All helpers use expressive defaults that make the role immediately obvious.

### **Fixture Naming and Organization**

#### **Avoid Fixture Name Shadowing**

When creating local fixtures, **NEVER shadow global fixtures** from `tests/fixtures/`.

**❌ WRONG: Shadowing Global Fixtures**

```python
# In test_ticket_api.py - local fixture shadows global one
@pytest.fixture
def org_admin_token(client: TestClient, organization: str, super_admin_token: str):
    # This shadows tests/fixtures/auth_fixtures.py::org_admin_token
    ...
```

**✅ CORRECT: Use Descriptive Prefix**

```python
# In test_ticket_api.py - clear, non-shadowing name
@pytest.fixture
def shared_org_admin_token(client: TestClient, organization: str, super_admin_token: str):
    """Create Admin user in shared organization and return token and org_id."""
    from tests.helpers import create_admin_user

    _, password = create_admin_user(client, super_admin_token, organization)
    response = client.post("/auth/login", json={"username": "admin", "password": password})
    return response.json()["access_token"], organization
```

#### **Global vs Local Fixtures**

**Global Fixtures** (`tests/fixtures/auth_fixtures.py`):
- Each creates its **own separate organization**
- Use when tests need **organization isolation**
- Examples: `org_admin_token`, `project_manager_token`, `write_user_token`

**Local Fixtures** (test file-specific):
- All users share **same organization**
- Use when tests need **cross-user scenarios** in same org
- **Prefix with context** (e.g., `shared_org_admin_token`)
- Common in ticket/project tests where multiple users collaborate

**Pattern for Shared-Org Fixtures:**

```python
# Note: Prefix with 'shared_org_' to indicate all users share same organization
@pytest.fixture
def shared_org_admin_token(client: TestClient, organization: str, super_admin_token: str):
    """Create Admin user in shared organization."""
    _, password = create_admin_user(client, super_admin_token, organization)
    response = client.post("/auth/login", json={"username": "admin", "password": password})
    return response.json()["access_token"], organization

@pytest.fixture
def shared_org_pm_token(client: TestClient, organization: str, super_admin_token: str):
    """Create Project Manager in shared organization."""
    _, password = create_project_manager(client, super_admin_token, organization)
    response = client.post("/auth/login", json={"username": "projectmanager", "password": password})
    return response.json()["access_token"], organization
```

#### **When to Create Local Fixtures**

Create local fixtures when:
- ✅ Multiple users need to be in the **same organization** for test scenarios
- ✅ Testing **cross-user interactions** (assigning tickets, viewing others' work)
- ✅ Testing **organization-scoped permissions** (can/cannot see other users' data)

Use global fixtures when:
- ✅ Each test needs **organization isolation**
- ✅ No cross-user scenarios in same org
- ✅ Standard permission/CRUD testing

## Core Testing Principles

### **Testing Guidelines**

A test should almost always test a single fact about the behavior of the code.

**Good example**: `test_after_create_get_returns_the_entity`

**Test scope**: Test behavior = cohesive whole = complete story. For example, to test create(), you also need to test get() to verify creation worked.

**Test behaviors, not implementations**: The "truth" of a component is its external observable behavior. Tests should verify that behavior as much as possible. If you created a test that uses implementation details like private members, ask yourself if you can write the test to verify the same behavior only using external API. If yes, re-write the test.

**Tests must be isolated** so they never interfere with each other.

**Tests must use clear language**: decisive, specific and explicit.

**Avoid using mocks**: Simulators for quick tests are fine (e.g., using in-memory SQLite instead of disk-based for performance).

**Test a variety of inputs**: Include variations on input data and edge cases.

**Test file names** should be significant, specific and descriptive of content:
- GOOD: `test_stub_entity_api.py`
- BAD: `test_task_03_stub_entity.py`
- BAD: `test_api.py`

## PyTest Fixtures

### **Available Test Fixtures**

All fixtures defined in `tests/conftest.py`:

**`db_path: str`**
- Configurable database path: disk (default) or `:memory:`
- Run with: `pytest` (disk) or `pytest --db-mode=memory` (memory)
- Each test gets isolated database

**`test_db: Database`**
- Initialized Database instance with tables
- Automatically creates/drops tables and disposes engine

**`test_session: Session`**
- SQLAlchemy session connected to test database
- Automatically commits and closes

**`test_stub_entity_repo: StubEntityRepository`**
- Repository instance ready for CRUD operations

**`client: TestClient`**
- FastAPI TestClient with test database dependency overrides
- **Use for all API tests**

### **Fixture Usage Examples**

**Repository Tests:**
```python
from tests.conftest import test_stub_entity_repo  # noqa: F401

class TestStubEntityRepository:
    def test_create_stub_entity(self, test_stub_entity_repo: StubEntityRepository) -> None:
        """Test creating a stub entity in the database."""
        # ... test code
```

**API Tests:**
```python
from fastapi.testclient import TestClient
from tests.conftest import client  # noqa: F401

class TestStubEntityAPI:
    def test_create_stub_entity(self, client: TestClient) -> None:
        """Test creating stub entity via API."""
        # ... test code
```

## Test File Organization

### **File Naming Conventions**
- **API Tests**: `test_[entity]_api.py`
- **Repository Tests**: `test_[entity]_repository.py`
- **Domain Tests**: `test_[model]_validation.py` (if needed)

### **Test Class Organization**
```python
class TestStubEntityAPIEndpoints:
    """Test all stub entity API endpoints for CRUD operations."""

    def test_create_stub_entity(self, client: TestClient) -> None:
        """Test successful stub entity creation."""

    def test_create_stub_entity_without_description(self, client: TestClient) -> None:
        """Test creation without optional field."""

    def test_get_stub_entity_by_id(self, client: TestClient) -> None:
        """Test successful stub entity retrieval."""

    def test_get_stub_entity_by_id_not_found(self, client: TestClient) -> None:
        """Test 404 for non-existent entity."""

class TestStubEntityAPICRUDWorkflow:
    """Test complete CRUD workflow for stub entities."""

    def test_complete_stub_entity_crud_workflow(self, client: TestClient) -> None:
        """Test complete workflow: create, read, update, delete."""
```

## Common Testing Patterns

### **Integration Over Isolation**
- **Prefer real HTTP requests** over mocking
- **Test actual database operations**
- **Validate complete request-response cycles**

### **Test Data Management**
- **Use unique values** to avoid test conflicts
- **Clean up happens automatically** via fixtures
- **Each test gets isolated database**

### **Complete Workflow Testing**
```python
def test_complete_stub_entity_crud_workflow(self, client: TestClient) -> None:
    """Test a complete CRUD workflow for a stub entity."""
    # 1. Create
    create_response = client.post("/stub_entities", json={
        "name": "Workflow Entity",
        "description": "Full CRUD test"
    })
    assert create_response.status_code == 201
    entity_id = create_response.json()["id"]

    # 2. Read
    get_response = client.get(f"/stub_entities/{entity_id}")
    assert get_response.status_code == 200

    # 3. List
    list_response = client.get("/stub_entities")
    assert len(list_response.json()) == 1

    # 4. Delete
    delete_response = client.delete(f"/stub_entities/{entity_id}")
    assert delete_response.status_code == 204

    # 5. Verify deletion
    final_get = client.get(f"/stub_entities/{entity_id}")
    assert final_get.status_code == 404
```

## Test Validation Rules

### **Before Completing Any Feature**
- [ ] All API endpoints have comprehensive tests
- [ ] Happy path scenarios covered
- [ ] Error conditions tested with proper status codes
- [ ] Complete workflows tested end-to-end
- [ ] All tests pass in isolation
- [ ] All tests pass when run together
- [ ] All fixtures explicitly imported

### **Test Quality Checklist**
- [ ] Test names are descriptive and specific
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Error messages are validated
- [ ] HTTP status codes are correct
- [ ] Response data structure is validated
- [ ] Tests are independent and isolated
- [ ] PyTest fixtures explicitly imported with `# noqa: F401`

**Remember: If the API works correctly in tests, users can accomplish their goals. No amount of perfect unit tests matters if the API doesn't work.**
