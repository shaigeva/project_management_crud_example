# Current Task List - Activity Logs & Audit Trails

**Created**: 2025-01-26
**Spec Reference**: [Activity Logs & Audit Trails](../spec/detailed/activity_logs_detailed_spec.md)

---

## Task 1: Activity log data structures and repository
**Status**: ⏳ Pending
**Implements**: Foundation for all REQ-ACTIVITY requirements

Create domain models, ORM models, and repository for activity logs. Implement basic CRUD operations (create, get by ID, list with filters).

---

## Task 2: Add activity logging to ticket operations
**Status**: ⏳ Pending
**Implements**: REQ-ACTIVITY-001
**Dependencies**: Task 1

Add logging to all ticket endpoints (create, update, status change, assign, move, delete).

---

## Task 3: Add activity logging to project operations
**Status**: ⏳ Pending
**Implements**: REQ-ACTIVITY-002
**Dependencies**: Task 1

Add logging to all project endpoints (create, update, archive, unarchive, delete).

---

## Task 4: Add activity logging to user operations
**Status**: ⏳ Pending
**Implements**: REQ-ACTIVITY-003
**Dependencies**: Task 1

Add logging to all user endpoints (create, update, role change, activate, deactivate, delete, password change).

---

## Task 5: Activity log query API with filtering and permissions
**Status**: ⏳ Pending
**Implements**: REQ-ACTIVITY-004, REQ-ACTIVITY-005, REQ-ACTIVITY-006, REQ-ACTIVITY-007
**Dependencies**: Task 1, Task 2, Task 3, Task 4

Create API endpoints for querying activity logs with filters (entity, actor, action, date range). Implement permission-based access control. Ensure logs are immutable (no update/delete endpoints).

---

## Completion

- [ ] All tasks marked ✅
- [ ] All REQ-ACTIVITY-001 through REQ-ACTIVITY-007 marked ✅ in specs
- [ ] Archive to `archive/2025-01-26_activity_logs.md`
