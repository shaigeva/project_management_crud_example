# Main Specification

This document contains high-level feature descriptions and rationale. Each feature links to a detailed specification.

See [how_to_write_specs.md](how_to_write_specs.md) for guidance on writing specifications and tests.

---

## Feature: Stub Entity Template
**Status**: 🟢 4/4 requirements implemented (100%)
**Detail Spec**: See existing stub entity implementation
**Purpose**: Template/scaffolding for creating real entities

### Rationale
Provides a complete, working example of all architectural layers (domain, repository, API, tests) that can be copied and adapted for new entities.

### High-Level Requirements
- ✅ REQ-STUB-001: Create and retrieve stub entities
- ✅ REQ-STUB-002: List all stub entities
- ✅ REQ-STUB-003: Delete stub entities
- ✅ REQ-STUB-004: Handle not-found errors appropriately

**Completion Date**: 2024-01-20 (Initial scaffolding)

---

## Feature: Project Management
**Status**: 🔴 0/8 requirements implemented (0%)
**Detail Spec**: [detailed/projects_detailed_spec.md](detailed/projects_detailed_spec.md)
**Purpose**: Allow users to create and manage projects

### Rationale
Projects are the core organizational unit. Users need to create projects, view their projects, update project details, and delete projects they no longer need.

### High-Level Requirements
- 🔴 REQ-PROJ-001: Create project and verify persistence
- 🔴 REQ-PROJ-002: Retrieve project by ID
- 🔴 REQ-PROJ-003: List all projects
- 🔴 REQ-PROJ-004: Update project details
- 🔴 REQ-PROJ-005: Delete project
- 🔴 REQ-PROJ-006: Handle not-found errors
- 🔴 REQ-PROJ-007: Handle validation errors
- 🔴 REQ-PROJ-008: Support project search/filtering

---

## Feature: Task Management
**Status**: 🔴 0/12 requirements implemented (0%)
**Detail Spec**: [detailed/tasks_detailed_spec.md](detailed/tasks_detailed_spec.md)
**Purpose**: Allow users to create and track tasks within projects

### Rationale
Tasks are the work items within projects. Users need to create tasks, assign them, track status, and mark them complete.

### High-Level Requirements
- 🔴 REQ-TASK-001: Create task within project
- 🔴 REQ-TASK-002: Retrieve task by ID
- 🔴 REQ-TASK-003: List tasks in project
- 🔴 REQ-TASK-004: Update task details
- 🔴 REQ-TASK-005: Update task status
- �4 REQ-TASK-006: Delete task
- 🔴 REQ-TASK-007: Task priority management
- 🔴 REQ-TASK-008: Task due dates
- 🔴 REQ-TASK-009: Task assignment
- 🔴 REQ-TASK-010: Filter tasks by status
- 🔴 REQ-TASK-011: Handle task-project relationship errors
- 🔴 REQ-TASK-012: Cascade delete when project deleted

---

## Status Legend

**Feature Status:**
- 🔴 Not Started (0% requirements implemented)
- 🟡 Partial (1-99% requirements implemented)
- 🟢 Fully Implemented (100% requirements implemented)

**Requirement Status:**
- 🔴 Not Implemented
- ✅ Implemented
- ⚠️ Implemented Incorrectly (needs fix)

**How to Update Status:**
- When a requirement is fully implemented and tested, change 🔴 → ✅
- Update feature status percentage and emoji based on completed requirements
- Status changes happen inline, no separate tracking file
