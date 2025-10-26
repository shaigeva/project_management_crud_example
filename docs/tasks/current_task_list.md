# Current Task List - Comments Feature

**Created**: 2025-01-26
**Spec Reference**: [Comments Detailed Spec](../spec/detailed/comments_detailed_spec.md)

---

## Task 1: Comment data model and repository layer
**Status**: ⏳ Pending
**Implements**: Foundation for REQ-COMMENT-001 through REQ-COMMENT-008

Create Comment entity, database model, and repository with CRUD operations.

---

## Task 2: Comment API endpoints
**Status**: ⏳ Pending
**Implements**: REQ-COMMENT-001, REQ-COMMENT-002, REQ-COMMENT-003, REQ-COMMENT-004, REQ-COMMENT-005
**Dependencies**: Task 1

Implement REST endpoints: POST /tickets/{id}/comments, GET /comments/{id}, GET /tickets/{id}/comments, PUT /comments/{id}, DELETE /comments/{id}.

---

## Task 3: Comment authorization and permissions
**Status**: ⏳ Pending
**Implements**: REQ-COMMENT-004, REQ-COMMENT-005, REQ-COMMENT-007, REQ-COMMENT-008
**Dependencies**: Task 2

Enforce author-only editing, author/admin deletion, organization scoping, and permission errors.

---

## Task 4: Comment metadata and validation
**Status**: ⏳ Pending
**Implements**: REQ-COMMENT-006, REQ-COMMENT-008
**Dependencies**: Task 2

Ensure automatic author tracking, timestamps, content validation (length limits, required fields).

---

## Completion

- [ ] All tasks marked ✅
- [ ] All REQ-COMMENT-001 through REQ-COMMENT-008 marked ✅ in specs
- [ ] Feature status in main_spec.md updated to 🟢 100%
- [ ] Archive to `archive/2025-01-26_comments.md`
