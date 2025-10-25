# Current Task List - Complete Projects Feature

**Created**: 2025-01-25
**Spec Reference**: [Projects](../spec/detailed/projects_detailed_spec.md)

---

## Task 1: Add project filtering/search (REQ-PROJ-009)
**Status**: ✅ Complete
**Implements**: REQ-PROJ-009

Add query parameters to GET /api/projects endpoint to filter projects by name (search) and is_active status.

**What was implemented**:
- Added optional query parameters: `name` (substring search), `is_active` (boolean filter)
- Implemented repository method `get_by_filters()` with organization_id, name, and is_active filtering
- Added comprehensive API tests (11 tests) covering all filter combinations
- Added comprehensive repository tests (9 tests) for filtering logic

**Completed**:
- ✅ GET /api/projects?name=backend returns projects with "backend" in name (case-insensitive)
- ✅ GET /api/projects?is_active=true returns only active projects
- ✅ GET /api/projects?name=api&is_active=true combines filters
- ✅ Filters work within organization scope (users still only see their org's projects)
- ✅ All validations pass (zero errors/warnings)

---

## Task 2: Add project soft delete/archive (REQ-PROJ-010)
**Status**: ✅ Complete
**Implements**: REQ-PROJ-010

Add archive functionality to allow soft deletion of projects rather than permanent removal.

**What was implemented**:
- Added `is_archived` (boolean) and `archived_at` (datetime) fields to ProjectORM and Project domain model
- Added repository methods: `archive()` and `unarchive()` in Projects class
- Updated repository filtering: `get_by_filters()` with `include_archived` parameter, updated `get_all()` and `get_by_organization_id()` to exclude archived by default
- Added PATCH /api/projects/{id}/archive endpoint (Admin, PM can access)
- Added PATCH /api/projects/{id}/unarchive endpoint (Admin only)
- Added `include_archived` query parameter to GET /api/projects
- Added comprehensive tests: 11 repository tests + 15 API tests

**Completed**:
- ✅ PATCH /api/projects/{id}/archive sets is_archived=true and archived_at=now
- ✅ Archived projects don't appear in GET /api/projects by default
- ✅ GET /api/projects?include_archived=true shows archived projects
- ✅ PATCH /api/projects/{id}/unarchive restores project (is_archived=false, archived_at=null)
- ✅ Admin and PM can archive projects
- ✅ Only Admin can unarchive projects
- ✅ All validations pass (zero errors/warnings)
- ℹ️ Cannot create tickets in archived projects - noted in spec as future validation (not implemented yet since depends on ticket creation logic)

---

## Completion

- [x] Task 1 marked ✅
- [x] REQ-PROJ-009 marked ✅ in spec
- [x] Updated main_spec.md status to 🟢 9/10 (90%)
- [x] Task 2 marked ✅
- [x] REQ-PROJ-010 marked ✅ in spec
- [x] Updated main_spec.md status to ✅ 10/10 (100%) - V1 Complete
- [ ] Archive to `archive/2025-01-26_complete_projects.md`
