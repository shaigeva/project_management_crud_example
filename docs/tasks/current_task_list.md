# Current Task List - Complete Projects Feature

**Created**: 2025-01-25
**Spec Reference**: [Projects](../spec/detailed/projects_detailed_spec.md)

---

## Task 1: Add project filtering/search (REQ-PROJ-009)
**Status**: ⏳ Pending
**Implements**: REQ-PROJ-009

Add query parameters to GET /api/projects endpoint to filter projects by name (search) and is_active status.

**What to implement**:
- Add optional query parameters: `name` (substring search), `is_active` (boolean filter)
- Update repository method to support filtering
- Add comprehensive tests for various filter combinations

**Acceptance criteria**:
- GET /api/projects?name=backend returns projects with "backend" in name (case-insensitive)
- GET /api/projects?is_active=true returns only active projects
- GET /api/projects?name=api&is_active=true combines filters
- Filters work within organization scope (users still only see their org's projects)

---

## Task 2: Add project soft delete/archive (REQ-PROJ-010)
**Status**: ⏳ Pending
**Implements**: REQ-PROJ-010

Add archive functionality to allow soft deletion of projects rather than permanent removal.

**What to implement**:
- Add `is_archived` (boolean) and `archived_at` (datetime) fields to database schema
- Add fields to domain models
- Add PATCH /api/projects/{id}/archive endpoint
- Add PATCH /api/projects/{id}/unarchive endpoint
- Filter archived projects from default listings (unless explicitly requested)
- Add optional `include_archived` query parameter to list endpoint
- Update delete endpoint to archive instead of hard delete (or keep separate)
- Add comprehensive tests for archive/unarchive workflows

**Acceptance criteria**:
- PATCH /api/projects/{id}/archive sets is_archived=true and archived_at=now
- Archived projects don't appear in GET /api/projects by default
- GET /api/projects?include_archived=true shows archived projects
- PATCH /api/projects/{id}/unarchive restores project (is_archived=false, archived_at=null)
- Cannot create tickets in archived projects
- Admin and PM can archive projects
- Only Admin can unarchive projects

---

## Completion

- [ ] All tasks marked ✅
- [ ] REQ-PROJ-009 marked ✅ in spec
- [ ] REQ-PROJ-010 marked ✅ in spec
- [ ] Update main_spec.md status to 🟢 10/10 (100%)
- [ ] Archive to `archive/2025-01-25_complete_projects.md`
