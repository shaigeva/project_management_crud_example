# Task Implementation Plan: Activity log data structures and repository

**Task Status**: 🔄 In Progress
**Date**: 2025-01-26
**Implements Requirements**: Foundation for all REQ-ACTIVITY-001 through REQ-ACTIVITY-007

## Behaviors to Implement

This task creates the foundational infrastructure for activity logging. It does NOT implement the actual logging (that comes in Tasks 2-4), nor the API endpoints (Task 5). This task focuses on:

1. Data structures to represent activity logs
2. Database schema for storing activity logs
3. Repository methods to create and query activity logs
4. Complete repository testing

### Foundation for REQ-ACTIVITY-001, 002, 003: Log entity changes

**Observable Behavior** (will be tested in Tasks 2-4):
- When entities are modified, activity log entries are created
- Each log entry captures: what changed, who did it, when it happened

**This Task's Contribution**:
- Provide ActivityLog domain model
- Provide ActivityLogCreateCommand for creating logs
- Provide repository methods to persist logs

### Foundation for REQ-ACTIVITY-004: Retrieve activity log for entity

**Observable Behavior** (will be tested in Task 5):
- GET /activity_logs?entity_type=ticket&entity_id=123 returns logs for that entity
- Logs ordered by timestamp

**This Task's Contribution**:
- Repository method: `list(entity_type=..., entity_id=...)`
- Returns logs in chronological order

### Foundation for REQ-ACTIVITY-005: Filter activity logs

**Observable Behavior** (will be tested in Task 5):
- Query parameters filter logs by: entity_type, entity_id, actor_id, action, date range, organization_id
- Multiple filters combine with AND logic

**This Task's Contribution**:
- Repository method: `list()` with all filter parameters
- Complex filtering logic in repository

### Foundation for REQ-ACTIVITY-006: Logs respect permissions

**Observable Behavior** (will be tested in Task 5):
- Users only see logs for entities they can access
- Organization-scoped by default

**This Task's Contribution**:
- Organization_id field in logs
- Repository can filter by organization

### Foundation for REQ-ACTIVITY-007: Logs are immutable

**Observable Behavior** (will be tested in Task 5):
- No PUT/DELETE endpoints for activity logs

**This Task's Contribution**:
- Repository has create() and list() methods only
- No update() or delete() methods

## Implementation Plan

### Domain Layer Changes

- [ ] Add ActionType enum in domain_models.py
  - Values: ticket_created, ticket_updated, ticket_status_changed, ticket_assigned, ticket_moved, ticket_deleted
  - Plus: project_created, project_updated, project_archived, project_unarchived, project_deleted
  - Plus: user_created, user_updated, user_role_changed, user_activated, user_deactivated, user_password_changed, user_deleted

- [ ] Add ActivityLog model in domain_models.py
  - Fields: id (str), entity_type (str), entity_id (str), action (ActionType), actor_id (str), organization_id (str), timestamp (datetime), changes (dict), metadata (Optional[dict])

- [ ] Add ActivityLogCreateCommand in domain_models.py
  - Fields: entity_type, entity_id, action, actor_id, organization_id, changes, metadata (optional)
  - Timestamp auto-set by repository

### Repository Layer Changes

- [ ] Add ActivityLogORM in orm_data_models.py
  - Table: activity_logs
  - Columns: id (String 36, PK), entity_type (String 50), entity_id (String 36), action (String 50), actor_id (String 36), organization_id (String 36), timestamp (DateTime), changes (Text), metadata (Text nullable)
  - Indexes: entity_type+entity_id, organization_id, actor_id, timestamp

- [ ] Add converters in converters.py
  - `orm_activity_log_to_domain_activity_log(orm_activity_log: ActivityLogORM) -> ActivityLog`
  - `orm_activity_logs_to_domain_activity_logs(orm_activity_logs: List[ActivityLogORM]) -> List[ActivityLog]`
  - Handle JSON deserialization for changes and metadata fields

- [ ] Add Repository.ActivityLogs nested class in repository.py
  - `create(command: ActivityLogCreateCommand) -> ActivityLog` - Create new log entry
  - `get_by_id(log_id: str) -> Optional[ActivityLog]` - Get single log by ID
  - `list(entity_type, entity_id, actor_id, action, from_date, to_date, organization_id, order) -> List[ActivityLog]` - List with filters

- [ ] Update Repository.__init__ to instantiate self.activity_logs

### Database Layer Changes

- [ ] Update database.py to include ActivityLogORM in metadata for table creation

### Other Changes

- [ ] JSON serialization: Use json.dumps/loads for changes and metadata (SQLite has no native JSON)

## Test Planning

### 2. Repository Layer Tests

**File**: tests/dal/test_activity_log_repository.py

**Tests for create() method** (3 tests):
- `test_create_activity_log` - Basic creation with all fields
- `test_create_activity_log_with_metadata` - Metadata preserved
- `test_create_activity_log_without_metadata` - Works without metadata

**Tests for get_by_id() method** (2 tests):
- `test_get_activity_log_by_id` - Retrieve by ID works
- `test_get_activity_log_by_id_not_found` - Returns None for missing

**Tests for list() - basic** (4 tests):
- `test_list_all_activity_logs` - Lists all when no filters
- `test_list_activity_logs_empty` - Returns [] when empty
- `test_list_activity_logs_ordered_ascending` - Default oldest first
- `test_list_activity_logs_ordered_descending` - order="desc" newest first

**Tests for list() - entity filters** (3 tests):
- `test_list_filter_by_entity_type` - Filter by ticket/project/user
- `test_list_filter_by_entity_id` - Filter by specific ID
- `test_list_filter_by_entity_type_and_id` - Combined filter

**Tests for list() - actor filter** (1 test):
- `test_list_filter_by_actor_id` - Filter by who did it

**Tests for list() - action filter** (1 test):
- `test_list_filter_by_action` - Filter by action type

**Tests for list() - date filters** (3 tests):
- `test_list_filter_by_from_date` - Logs after date
- `test_list_filter_by_to_date` - Logs before date
- `test_list_filter_by_date_range` - Logs within range

**Tests for list() - organization filter** (1 test):
- `test_list_filter_by_organization_id` - Org scoping

**Tests for list() - combined** (1 test):
- `test_list_multiple_filters_combined` - AND logic for filters

**Tests for changes field** (2 tests):
- `test_activity_log_changes_preserved` - Complex dict preserved
- `test_activity_log_changes_with_null_values` - Null values work

**Total: ~21 repository tests**

### 3. Converter Tests

**File**: tests/dal/test_converters.py

**Activity log converter tests** (3 tests):
- `test_orm_activity_log_to_domain` - Basic conversion
- `test_orm_activity_log_with_null_metadata` - Handles None metadata
- `test_orm_activity_logs_list_conversion` - List converter

### Repository Helper Function

**File**: tests/dal/helpers.py

Add:
```python
def create_test_activity_log_via_repo(
    test_repo: Repository,
    entity_type: str = "ticket",
    entity_id: str = "test-entity-id",
    action: ActionType = ActionType.TICKET_CREATED,
    actor_id: str = "test-user-id",
    organization_id: str = "test-org-id",
    changes: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> ActivityLog
```

## Technical Notes

### JSON Storage

SQLite doesn't have native JSON. Use Text columns with json.dumps/loads:

```python
# Repository create
import json
orm_log.changes = json.dumps(command.changes)

# Converter
changes=json.loads(orm_log.changes)
```

### Indexes

Add for query performance:
```python
Index('idx_activity_logs_entity', 'entity_type', 'entity_id')
Index('idx_activity_logs_organization', 'organization_id')
Index('idx_activity_logs_actor', 'actor_id')
Index('idx_activity_logs_timestamp', 'timestamp')
```

### Action Types (Enum)

```python
class ActionType(str, Enum):
    # Tickets
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    TICKET_STATUS_CHANGED = "ticket_status_changed"
    TICKET_ASSIGNED = "ticket_assigned"
    TICKET_MOVED = "ticket_moved"
    TICKET_DELETED = "ticket_deleted"

    # Projects
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_ARCHIVED = "project_archived"
    PROJECT_UNARCHIVED = "project_unarchived"
    PROJECT_DELETED = "project_deleted"

    # Users
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_ROLE_CHANGED = "user_role_changed"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    USER_PASSWORD_CHANGED = "user_password_changed"
    USER_DELETED = "user_deleted"
```

### Changes Structure Examples

**Create**: Single-level with created data
**Update**: Field-level old/new values
**Delete**: Snapshot of deleted entity

## Implementation Checklist

Domain Layer:
- [ ] ActionType enum
- [ ] ActivityLog model
- [ ] ActivityLogCreateCommand

ORM Layer:
- [ ] ActivityLogORM with indexes
- [ ] Update database.py

Converter Layer:
- [ ] Converters with JSON handling

Repository Layer:
- [ ] ActivityLogs nested class
- [ ] create(), get_by_id(), list() methods
- [ ] Update Repository.__init__

Testing:
- [ ] ~21 repository tests
- [ ] 3 converter tests
- [ ] Repository helper function
- [ ] Run validations

Status Updates:
- [ ] Mark task ✅ in current_task_list.md
