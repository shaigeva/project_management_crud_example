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

## Testing Priority Hierarchy

### **Priority 1: API Endpoint Tests (Critical) ⭐⭐⭐**

**Why Critical**: Test actual user-facing functionality and complete request-response cycles

**Location**: `tests/api/test_*_api.py`

**Required Coverage**:
- ✅ **Happy path scenarios**: Valid requests, correct responses, proper HTTP status codes
- ✅ **Error handling**: 422 validation, 404 not found, 400 business logic violations
- ✅ **Complete workflows**: Multi-step user scenarios, data persistence

### **Priority 2: Repository/DAL Tests (Important) ⭐⭐**

**Location**: `tests/dal/test_*_repository.py`

**Coverage**: CRUD operations, database interactions, data persistence

### **Priority 3: Domain Logic Tests (Supporting) ⭐**

**Location**: `tests/data_models/` (if needed)

**Coverage**: Pydantic model validation, business rules, data transformations

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
