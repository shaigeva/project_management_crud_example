# How to Write Specifications and Tests

This guide defines how to write behavioral specifications and corresponding tests in this project.

## How to Update Specifications

### Specification File Structure

**Main spec** (`docs/spec/main_spec.md`):
- High-level feature list
- Rationale for each feature
- Status and requirement counts (inline)
- Links to detailed specs

**Detailed specs** (`docs/spec/detailed/feature_xxx_detailed_spec.md`):
- Detailed requirements with unique IDs (REQ-XXX-YYY)
- Scenario descriptions
- Observable behaviors
- Explicit test specifications
- Edge cases
- Status for each requirement (inline)

### Requirement Format

Each requirement must have:

1. **Unique ID**: `REQ-{FEATURE}-{NUMBER}`
   - Example: REQ-PROJ-001, REQ-TASK-003

2. **Status** (inline): 🔴 Not Implemented | ✅ Implemented | ⚠️ Needs Fix

3. **Type**: Product Behavior (preferred) or Technical Behavior (if necessary)

4. **Scenario**: Explicit description of when this behavior occurs

5. **Observable Behavior**: What external systems can verify

6. **Test Specification**: Explicit test names with descriptions

7. **Edge Cases**: List of edge cases to test

### Status Tracking (Inline Only)

**No separate tracking files.** Status lives in spec files:

- Each requirement has its own status marker
- Feature status calculated from requirements (e.g., "🟡 4/8 implemented")
- Update status when behavior is implemented and tested

## Core Principle: Product Behavior Over Technical Details

### What is Product Behavior?

**Product behavior** is what users or external systems can observe and verify.
**Technical details** are implementation choices that users cannot observe.

**Examples:**

✅ **GOOD - Product Behavior:**
- "After creating a project, GET /projects/{id} returns that project"
- "When a user submits invalid data, the API returns 400 with error details"
- "After deleting a project, attempting to GET it returns 404"
- "Creating two projects with the same name succeeds (both are created)"

❌ **BAD - Technical Details:**
- "Project is written to the database"
- "The projects table has a row inserted"
- "The ORM model is persisted"
- "Returns 201 status code" (alone, without behavioral consequence)

### Why Product Behavior Matters

**Product behavior tests are robust:**
- They verify what users actually care about
- They don't break when implementation changes (e.g., switching databases)
- They test through the external API, proving the system works

**Technical detail tests are fragile:**
- They break when you rename a table or change internal structure
- They test things users cannot observe
- They don't prove the product actually works

### The "So What?" Test

When writing a requirement, ask: **"So what? How would a user/external system know this happened?"**

❌ **"When user creates a project, it returns 201"**
- So what? What can the user DO with that information?

✅ **"When user creates a project, they receive a project ID that can be used to retrieve the project later"**
- This is testable through external API
- This is what users need to accomplish their goals

## How to Write Requirements

### Requirement Structure

Each requirement must have:

1. **Unique ID**: `REQ-{FEATURE}-{NUMBER}`
2. **Status**: 🔴 Not Implemented | ✅ Implemented | ⚠️ Needs Fix
3. **Type**: Product Behavior (preferred) or Technical Behavior (if necessary)
4. **Scenario**: When does this happen?
5. **Observable Behavior**: What can external systems observe?
6. **Test Specification**: Explicit description of tests needed

### Template

```markdown
### REQ-XXX-001: [Short description of product behavior]
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

**Scenario**:
When [user/system action occurs]

**Observable Behavior**:
- [What happens that can be verified externally]
- [What API calls would prove this worked]
- [What state changes are observable]

**Test Specification**:
1. **Test**: `test_after_creating_project_get_returns_the_project`
   - **Verifies**: Created project is retrievable via GET
   - **Steps**: POST /projects → capture ID → GET /projects/{id} → verify data matches

2. **Test**: `test_created_project_appears_in_list`
   - **Verifies**: Created project appears in GET /projects list
   - **Steps**: POST /projects → GET /projects → verify new project is in list
```

### Example: Good Product Behavior Requirement

```markdown
### REQ-PROJ-001: Project creation and retrieval
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

**Scenario**:
When a user creates a project with valid data (name, description)

**Observable Behavior**:
- User receives a response containing the created project with a unique ID
- Subsequent GET request to /projects/{id} returns the same project
- The project appears in the list returned by GET /projects
- Project data (name, description) matches what was submitted
- Project includes timestamps (created_at, updated_at)

**Test Specification**:
1. **Test**: `test_after_create_project_get_by_id_returns_the_project`
   - **Verifies**: Created project can be retrieved by ID
   - **Steps**:
     - POST /projects with valid data
     - Capture project ID from response
     - GET /projects/{id}
     - Assert returned project matches created data

2. **Test**: `test_after_create_project_appears_in_list`
   - **Verifies**: Created project appears in full project list
   - **Steps**:
     - POST /projects with unique name
     - GET /projects
     - Assert project with that name is in the list

3. **Test**: `test_create_project_returns_project_with_id_and_timestamps`
   - **Verifies**: Creation response includes all expected fields
   - **Steps**:
     - POST /projects
     - Assert response includes: id, name, description, created_at, updated_at
     - Assert id is non-empty
     - Assert timestamps are valid datetime values

**Edge Cases to Test**:
- Creating project with minimal data (only required fields)
- Creating project with maximum length name
- Creating multiple projects with same name (should all succeed)
- Creating project with special characters in name
```

### Example: Bad Requirement (Too Technical)

❌ **DON'T DO THIS:**

```markdown
### REQ-PROJ-001: Project is saved to database
**Scenario**: When user POSTs to /projects
**Behavior**:
- ProjectORM instance is created
- Row is inserted into projects table
- Returns 201 status code

**Tests**:
- Check database has new row
- Verify ORM model is persisted
```

**Why this is bad:**
- "Row is inserted into projects table" - implementation detail
- "ProjectORM instance" - internal implementation
- Tests would query database directly - fragile
- Doesn't prove user can DO anything with the created project

## How to Write Test Specifications

### Test Specification Format

For each requirement, specify explicit tests:

```markdown
**Test Specification**:
1. **Test**: `test_name_that_describes_behavior`
   - **Verifies**: What product behavior this proves
   - **Steps**: Explicit steps to verify behavior
   - **Assertions**: What must be true for test to pass

2. **Test**: `test_edge_case_name`
   - **Verifies**: What edge case this covers
   - **Steps**: ...
```

### Test Naming Convention

Test names should describe **what behavior is verified**, not implementation:

✅ **GOOD:**
- `test_after_create_project_get_returns_the_project`
- `test_delete_project_makes_it_not_found`
- `test_update_project_name_changes_what_get_returns`
- `test_create_with_duplicate_name_succeeds` (if duplicates allowed)

❌ **BAD:**
- `test_create_project` (what about it?)
- `test_database_insert` (implementation detail)
- `test_201_response` (technical detail, not behavior)

### Test Implementation Guidelines

**Tests MUST:**
- Verify behavior through external API only (HTTP endpoints)
- Use the same API users/external systems would use
- Verify complete user workflows (create → verify can retrieve)
- Test edge cases defined in spec

**Tests MUST NOT:**
- Query database directly to verify state
- Check internal variables or private methods
- Depend on table names, column names, or schema
- Assume specific ORM implementation

**Example - Good Test:**
```python
def test_after_create_project_get_returns_the_project(self, client: TestClient) -> None:
    """Verify created project is retrievable via GET endpoint."""
    # Create project
    create_data = {"name": "Test Project", "description": "Test"}
    create_response = client.post("/projects", json=create_data)
    project_id = create_response.json()["id"]

    # Verify it can be retrieved
    get_response = client.get(f"/projects/{project_id}")

    assert get_response.status_code == 200
    project = get_response.json()
    assert project["id"] == project_id
    assert project["name"] == "Test Project"
    assert project["description"] == "Test"
```

**Example - Bad Test (Don't Do This):**
```python
def test_create_project_inserts_to_database(self, test_db: Database) -> None:
    """DON'T DO THIS - queries database directly"""
    # This is fragile and tests implementation, not behavior
    result = test_db.execute("SELECT * FROM projects WHERE name='Test'")
    assert result is not None  # BAD - depends on table structure
```

## Product vs Technical Behavior

### When Technical Details Are Acceptable

Sometimes you need to test technical behavior, but it should be **minimal** and **justified**:

**Acceptable technical tests:**
- Performance characteristics (response time under load)
- Resource cleanup (no memory leaks, connections closed)
- Security properties (passwords are hashed, not stored plain)

**Even then, prefer testing through observable behavior:**
- Instead of "password is hashed in database" → "cannot login with hash as password"
- Instead of "connection is closed" → "can make 1000 requests without errors"

### Hierarchy of Test Quality

1. **Best**: Product behavior via external API
   - `test_after_create_project_get_returns_it`

2. **Good**: Observable behavior via public interface
   - `test_repository_create_then_get_returns_same_data`

3. **Acceptable**: Technical behavior when necessary
   - `test_database_connections_are_disposed`

4. **Bad**: Implementation details that are fragile
   - `test_project_table_has_row` ← DON'T DO THIS

## Edge Cases and Test Coverage

### What to Test

For each requirement, tests must cover:

1. **Happy path** - Normal, valid usage
2. **Error conditions** - Invalid input, not found, conflicts
3. **Boundary values** - Min/max lengths, empty values, nulls
4. **Edge cases from spec** - Concurrent access, special characters, etc.

### Example Edge Case Coverage

```markdown
**Test Specification for REQ-PROJ-001**:

**Happy Path:**
- Create with all fields → verify retrievable
- Create with minimal fields → verify retrievable

**Error Conditions:**
- Create with missing required field → 400 error
- Create with invalid data type → 400 error
- GET non-existent project → 404 error

**Boundary Values:**
- Create with maximum length name → succeeds
- Create with empty description (if optional) → succeeds
- Create with 1-character name → succeeds or fails per validation rules

**Edge Cases:**
- Create with special characters in name → succeeds
- Create with unicode characters → succeeds
- Create two projects with identical data → both succeed
```

## Summary: The Rules

### For Specifications

1. ✅ **Focus on product behavior** - what users observe
2. ❌ **Avoid technical details** - implementation is flexible
3. ✅ **Specify explicit test requirements** - name + what it verifies
4. ✅ **Include edge cases** - don't leave to interpretation
5. ✅ **Status is inline** - no separate tracking files

### For Tests

1. ✅ **Test through external API** - HTTP endpoints
2. ❌ **Don't query database directly** - fragile and not observable
3. ✅ **Verify complete workflows** - create → retrieve → verify
4. ✅ **Test names describe behavior** - not implementation
5. ✅ **Cover all scenarios from spec** - happy path + edge cases

### The Golden Rule

**If a user or external system cannot observe it, don't specify it or test it directly.**

Test the **externally observable consequences** of internal behavior.
