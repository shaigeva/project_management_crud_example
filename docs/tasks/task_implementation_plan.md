# Task Implementation Plan: Add Project Archive/Soft Delete

**Task Status**: 🔄 In Progress
**Date**: 2025-01-26
**Implements Requirements**: REQ-PROJ-010

## Behaviors to Implement

### From REQ-PROJ-010: Archive projects (soft delete)
**Observable Behavior**:
- Projects can be archived instead of permanently deleted
- Archived projects don't appear in default listings
- Archived projects can be included in listings with explicit parameter
- Archived projects can be unarchived to restore them
- Archive/unarchive operations record timestamps
- Permission-based access to archive/unarchive operations

**Acceptance Criteria**:
- PATCH /api/projects/{id}/archive sets is_archived=true and archived_at=now
- Archived projects don't appear in GET /api/projects by default
- GET /api/projects?include_archived=true shows archived projects
- PATCH /api/projects/{id}/unarchive restores project (is_archived=false, archived_at=null)
- Cannot create tickets in archived projects (future requirement - note in tests)
- Admin and PM can archive projects
- Only Admin can unarchive projects

## Implementation Plan

### Domain Layer Changes
- [x] Add `is_archived: bool` field to Project domain model (default False)
- [x] Add `archived_at: Optional[datetime]` field to Project domain model

### Repository Layer Changes
- [x] Add `is_archived` and `archived_at` columns to ProjectORM model
- [x] Update `orm_project_to_domain_project` converter to include new fields
- [x] Add `archive(project_id: str) -> Optional[Project]` method to Projects repository
- [x] Add `unarchive(project_id: str) -> Optional[Project]` method to Projects repository
- [x] Update `get_by_filters()` to support `include_archived` parameter (default False)
- [x] Update `get_all()` and `get_by_organization_id()` to exclude archived by default

### API Layer Changes
- [x] Add PATCH /api/projects/{id}/archive endpoint (Admin, PM can access)
- [x] Add PATCH /api/projects/{id}/unarchive endpoint (Admin only)
- [x] Update GET /api/projects to add `include_archived` query parameter (default False)
- [x] Add organization scoping checks for archive/unarchive
- [x] Add proper error handling (404, 403)

### Database Migration
- [x] Add migration or schema update for new columns (SQLite auto-handles via ORM)

## Test Planning

### 1. API Tests (External Behavior)
**File**: tests/api/test_project_api.py

**New test class: TestArchiveProject**:
- `test_archive_project_as_admin`
  - Verifies: Admin can archive project
  - Steps: Create project → PATCH /archive → verify is_archived=true, archived_at set

- `test_archive_project_as_project_manager`
  - Verifies: PM can archive project
  - Steps: Create project as PM → PATCH /archive → verify success

- `test_archive_project_as_write_user_fails`
  - Verifies: Write user cannot archive
  - Steps: PATCH /archive as write user → assert 403

- `test_archive_project_from_different_org_fails`
  - Verifies: Cannot archive project from other org
  - Steps: Create project in org1 → archive from org2 → assert 403

- `test_archive_nonexistent_project_returns_404`
  - Verifies: Archiving non-existent project returns 404
  - Steps: PATCH /archive with fake ID → assert 404

- `test_archived_project_not_in_default_list`
  - Verifies: Archived projects excluded from default GET /projects
  - Steps: Create 2 projects → archive 1 → GET /projects → verify only 1 returned

- `test_archived_project_included_with_parameter`
  - Verifies: include_archived=true shows archived projects
  - Steps: Create project → archive → GET /projects?include_archived=true → verify shown

- `test_list_only_archived_projects`
  - Verifies: Can list only archived projects
  - Steps: Create active and archived → GET /projects?include_archived=true&is_active=false → verify only archived

- `test_archive_already_archived_project_succeeds`
  - Verifies: Archiving already archived project is idempotent
  - Steps: Archive → archive again → verify success

**New test class: TestUnarchiveProject**:
- `test_unarchive_project_as_admin`
  - Verifies: Admin can unarchive project
  - Steps: Create → archive → PATCH /unarchive → verify is_archived=false, archived_at=null

- `test_unarchive_project_as_project_manager_fails`
  - Verifies: PM cannot unarchive (only Admin)
  - Steps: Create/archive as PM → unarchive as PM → assert 403

- `test_unarchive_project_from_different_org_fails`
  - Verifies: Cannot unarchive project from other org
  - Steps: Create/archive in org1 → unarchive from org2 → assert 403

- `test_unarchive_nonexistent_project_returns_404`
  - Verifies: Unarchiving non-existent project returns 404
  - Steps: PATCH /unarchive with fake ID → assert 404

- `test_unarchive_active_project_succeeds`
  - Verifies: Unarchiving non-archived project is idempotent
  - Steps: Create (not archived) → PATCH /unarchive → verify success

- `test_unarchived_project_appears_in_default_list`
  - Verifies: Unarchived project appears in default listing
  - Steps: Create → archive → unarchive → GET /projects → verify present

**Existing tests to update**:
- None required - existing tests should still pass as archived behavior is additive

**Edge Cases**:
- Archive already archived project (idempotent)
- Unarchive already active project (idempotent)
- Filter combinations: include_archived with name/is_active filters
- Super Admin can archive/unarchive across organizations

### 2. Repository Layer Tests
**File**: tests/dal/test_project_repository.py

**New test class: TestProjectRepositoryArchive**:
- `test_archive_project_sets_fields`
  - Verifies: archive() sets is_archived=true and archived_at
  - Uses: repository.projects.archive(project_id) → verify fields set

- `test_archive_project_not_found_returns_none`
  - Verifies: Archiving non-existent project returns None
  - Uses: repository.projects.archive("fake-id") → assert None

- `test_archive_project_persists`
  - Verifies: Archived state persists in database
  - Uses: create → archive → get_by_id → verify is_archived=true

- `test_unarchive_project_clears_fields`
  - Verifies: unarchive() sets is_archived=false and archived_at=null
  - Uses: create → archive → unarchive → verify fields cleared

- `test_unarchive_project_not_found_returns_none`
  - Verifies: Unarchiving non-existent project returns None
  - Uses: repository.projects.unarchive("fake-id") → assert None

- `test_get_by_filters_excludes_archived_by_default`
  - Verifies: get_by_filters() excludes archived projects by default
  - Uses: create 2 → archive 1 → get_by_filters() → verify 1 returned

- `test_get_by_filters_includes_archived_when_requested`
  - Verifies: get_by_filters(include_archived=true) includes archived
  - Uses: create 2 → archive 1 → get_by_filters(include_archived=true) → verify 2 returned

- `test_get_by_filters_archived_only`
  - Verifies: Can filter for only archived projects
  - Uses: create active and archived → filter is_archived=true, include_archived=true → verify only archived

- `test_get_all_excludes_archived_by_default`
  - Verifies: get_all() excludes archived projects
  - Uses: create 2 → archive 1 → get_all() → verify 1 returned

- `test_get_by_organization_id_excludes_archived`
  - Verifies: get_by_organization_id() excludes archived
  - Uses: create 2 in org → archive 1 → get_by_organization_id() → verify 1 returned

### 3. Utility/Logic Tests
Not applicable for this task.

### 4. Domain Model Validation Tests
Not applicable - using simple boolean and optional datetime fields.

## Existing Tests to Update

No existing tests need updates - archive functionality is additive and doesn't break existing behavior.

## Dependencies

**Requires completion of**:
- Task 1 (complete ✅)

**Blocks**:
- None

## Notes

- Archive is a soft delete - project data remains in database
- Hard delete endpoint (DELETE /projects/{id}) remains available for Admin
- Future ticket creation validation will need to check is_archived field
- archived_at timestamp helps with audit trails and potential auto-cleanup policies
- include_archived parameter allows viewing historical data when needed
