# Main Specification - Multi-Tenant Project Management System

This document contains high-level feature descriptions and rationale. Each feature links to a detailed specification.

See [how_to_write_specs.md](how_to_write_specs.md) for guidance on writing specifications.

---

## Project Overview

A multi-tenant project management backend system supporting:
- Organizations (tenants) with isolated data
- Role-based access control (Admin, Project Manager, Write Access, Read Access)
- Projects containing tickets
- Epics that span multiple projects
- Comments on tickets
- Activity logs and audit trails with permission-based access
- Custom workflows (define ticket statuses per project)

---

## Feature: Stub Entity Template
**Status**: 🟢 4/4 requirements implemented (100%)
**Detail Spec**: See existing stub entity implementation
**Purpose**: Template/scaffolding for creating real entities
**Version**: N/A (scaffolding)

### Rationale
Provides a complete, working example of all architectural layers that can be copied and adapted for new entities.

### High-Level Requirements
- ✅ REQ-STUB-001: Create and retrieve stub entities
- ✅ REQ-STUB-002: List all stub entities
- ✅ REQ-STUB-003: Delete stub entities
- ✅ REQ-STUB-004: Handle not-found errors appropriately

**Completion Date**: 2024-01-20

---

## Feature: User Authentication
**Status**: 🟢 6/6 requirements implemented (100%)
**Detail Spec**: [detailed/auth_detailed_spec.md](detailed/auth_detailed_spec.md)
**Purpose**: Secure user authentication and session management
**Version**: V1

### Rationale
Users need secure authentication to access the system. Password-based login with bearer token sessions provides a balance of security and usability. Users receive generated passwords initially and can change them.

### High-Level Requirements
- ✅ REQ-AUTH-001: User login with username/password
- ✅ REQ-AUTH-002: Issue bearer token on successful login
- ✅ REQ-AUTH-003: Validate bearer token on protected endpoints
- ✅ REQ-AUTH-004: User can change their password
- ✅ REQ-AUTH-005: Token expiration and refresh
- ✅ REQ-AUTH-006: Handle authentication errors (invalid credentials, expired tokens)

**Notes**: Complete authentication feature with login, token-based sessions, password change, token expiration, and comprehensive error handling. Users can change passwords with strength validation (8+ chars, upper/lower/digit/special). Tokens remain stateless and valid after password changes.

---

## Feature: User Management
**Status**: 🟢 8/8 requirements implemented (100%)
**Detail Spec**: [detailed/users_detailed_spec.md](detailed/users_detailed_spec.md)
**Purpose**: Administer users within the system
**Version**: V1

### Rationale
Administrators need to create, update, and manage users. Users are created with generated passwords and assigned to organizations with specific roles.

### High-Level Requirements
- ✅ REQ-USER-001: Create user with generated password
- ✅ REQ-USER-002: Assign user to organization with role
- ✅ REQ-USER-003: Update user details
- ✅ REQ-USER-004: Deactivate/activate user
- ✅ REQ-USER-005: Delete user
- ✅ REQ-USER-006: List users (with filtering by org/role)
- ✅ REQ-USER-007: Retrieve user details
- ✅ REQ-USER-008: Handle user not found errors

**Notes**: Complete user CRUD with role-based authorization. Super Admin can manage all users; Org Admin can manage users in their organization. Password generation returns secure 12+ char passwords. Delete operation prevents removal of users who have created tickets.

---

## Feature: Multi-Tenancy (Organizations)
**Status**: 🟢 6/6 requirements implemented (100%)
**Detail Spec**: [detailed/organizations_detailed_spec.md](detailed/organizations_detailed_spec.md)
**Purpose**: Isolate data between different organizations (tenants)
**Version**: V1

### Rationale
The system supports multiple organizations (tenants) with complete data isolation. Each organization has its own projects, tickets, and users. Users can only access data within their organization.

### High-Level Requirements
- ✅ REQ-ORG-001: Create organization
- ✅ REQ-ORG-002: Retrieve organization details
- ✅ REQ-ORG-003: Update organization
- ✅ REQ-ORG-004: List organizations (admin only)
- ✅ REQ-ORG-005: Data isolation between organizations
- ✅ REQ-ORG-006: Users cannot access other organizations' data

**Notes**: Complete multi-tenant isolation implemented across all resources (projects, tickets, users). All list endpoints filter by user's organization. Cross-organization access attempts return 403 (projects/tickets) or 404 (users) to prevent information leakage. Super Admins can access all organizations. 14 comprehensive tests verify isolation boundaries.

---

## Feature: Role-Based Access Control
**Status**: 🟢 10/10 requirements implemented (100%)
**Detail Spec**: [detailed/rbac_detailed_spec.md](detailed/rbac_detailed_spec.md)
**Purpose**: Control access to resources based on user roles
**Version**: V1

### Rationale
Different users need different levels of access. The system supports five roles:
- **Super Admin**: Manage organizations, cross-organization access, create organization admins
- **Admin**: Full organization access, user management within organization
- **Project Manager**: Manage projects, tickets, assign users within organization
- **Write Access**: Create/update tickets and comments within organization
- **Read Access**: View tickets and comments only within organization

### High-Level Requirements
- ✅ REQ-RBAC-001: Super Admin can manage organizations and create organization admins
- ✅ REQ-RBAC-002: Super Admin can access all organizations
- ✅ REQ-RBAC-003: Admin role has full access within their organization
- ✅ REQ-RBAC-004: Project Manager can manage projects and tickets
- ✅ REQ-RBAC-005: Write Access users can create/update tickets
- ✅ REQ-RBAC-006: Read Access users can only view
- ✅ REQ-RBAC-007: Enforce permissions on all endpoints
- ✅ REQ-RBAC-008: Return 403 for unauthorized actions
- ✅ REQ-RBAC-009: Users see only data they have permission for
- ✅ REQ-RBAC-010: Activity logs reflect user permissions

**Notes**: Complete RBAC implementation with all five roles (Super Admin, Admin, Project Manager, Write Access, Read Access), comprehensive permission enforcement on 23 endpoints, organization-scoped data access, and 125+ permission tests. Activity log permissions implemented: Super Admin sees all logs, other roles see only their organization's logs.

---

## Feature: Projects
**Status**: 🟢 11/11 requirements implemented (100%)
**Detail Spec**: [detailed/projects_detailed_spec.md](detailed/projects_detailed_spec.md)
**Purpose**: Organize work into projects
**Version**: V1

### Rationale
Projects (e.g., "Backend", "Frontend") are containers for tickets. Users with appropriate permissions can create and manage projects within their organization.

### High-Level Requirements
- ✅ REQ-PROJ-001: Create project within organization
- ✅ REQ-PROJ-002: Retrieve project by ID
- ✅ REQ-PROJ-003: List projects in organization
- ✅ REQ-PROJ-004: Update project details
- ✅ REQ-PROJ-005: Delete project (with confirmation)
- ✅ REQ-PROJ-006: Projects are organization-scoped
- ✅ REQ-PROJ-007: Handle not-found errors
- ✅ REQ-PROJ-008: Handle validation errors
- ✅ REQ-PROJ-009: Filter/search projects
- ✅ REQ-PROJ-010: Archive projects (soft delete)
- ✅ REQ-PROJ-011: Projects reference workflows

**Notes**: Complete project management with CRUD operations, role-based authorization (Admin, PM can create/update/archive; Admin can delete/unarchive), organization scoping, filtering by name and is_active status, and archive/soft delete functionality with include_archived parameter for listings. Workflow integration (REQ-PROJ-011) fully implemented with 6 comprehensive tests verifying workflow references, validation, and ticket compatibility.

---

## Feature: Tickets
**Status**: 🟢 17/17 requirements implemented (100%)
**Detail Spec**: [detailed/tickets_detailed_spec.md](detailed/tickets_detailed_spec.md)
**Purpose**: Track work items within projects
**Version**: V1

### Rationale
Tickets are the core work items. They have a predefined set of fields (V1), belong to a project, can be moved between projects, and follow workflow-based status validation.

### High-Level Requirements
- ✅ REQ-TICKET-001: Create ticket in project
- ✅ REQ-TICKET-002: Retrieve ticket by ID
- ✅ REQ-TICKET-003: List tickets (with filtering)
- ✅ REQ-TICKET-004: Update ticket fields
- ✅ REQ-TICKET-005: Change ticket status (TODO/IN-PROGRESS/DONE)
- ✅ REQ-TICKET-006: Move ticket to different project
- ✅ REQ-TICKET-007: Assign ticket to user
- ✅ REQ-TICKET-008: Delete ticket
- ✅ REQ-TICKET-009: Tickets have predefined fields (title, description, status, priority, assignee, reporter, created/updated timestamps)
- ✅ REQ-TICKET-010: Filter tickets by status, assignee, project
- ✅ REQ-TICKET-011: Tickets are organization-scoped
- ✅ REQ-TICKET-012: Handle not-found errors
- ✅ REQ-TICKET-013: Handle validation errors
- ✅ REQ-TICKET-014: Ticket status workflow validation (basic - hardcoded enum)
- ✅ REQ-TICKET-015: Activity log for ticket changes
- ✅ REQ-TICKET-016: Validate status against project workflow (custom workflows)
- ✅ REQ-TICKET-017: Validate workflow when moving tickets between projects

**Notes**: Complete ticket management with 9 REST endpoints including specialized operations (status change, project moves, assignments). Role-based authorization implemented (Admin/PM/Write can create/update, Admin/PM can assign/move, Admin can delete). Organization scoping enforced via project relationships. Activity logging implemented for all 6 ticket operations (create, update, status change, assign, move, delete). Custom workflow integration (REQ-TICKET-16, REQ-TICKET-017) fully implemented with 8 comprehensive tests in test_custom_workflow_validation.py verifying workflow-based status validation, status defaults, and cross-project moves.

---

## Feature: Epics
**Status**: 🟢 10/10 requirements implemented (100%) - V1 Complete
**Detail Spec**: [detailed/epics_detailed_spec.md](detailed/epics_detailed_spec.md)
**Purpose**: Group related tickets across multiple projects
**Version**: V1

### Rationale
Epics provide a way to group related tickets that may span multiple projects. An epic represents a larger initiative or feature that comprises multiple tickets.

### High-Level Requirements
- ✅ REQ-EPIC-001: Create epic within organization
- ✅ REQ-EPIC-002: Retrieve epic by ID
- ✅ REQ-EPIC-003: List epics in organization
- ✅ REQ-EPIC-004: Update epic details
- ✅ REQ-EPIC-005: Delete epic
- ✅ REQ-EPIC-006: Add ticket to epic
- ✅ REQ-EPIC-007: Remove ticket from epic
- ✅ REQ-EPIC-008: List tickets in epic (from multiple projects)
- ✅ REQ-EPIC-009: Epics are organization-scoped
- ✅ REQ-EPIC-010: Handle validation and not-found errors

**Notes**: Complete epic management with CRUD operations, role-based authorization (Admin, PM can create/update/add/remove tickets; Admin can delete), organization scoping, and many-to-many ticket associations. Supports tickets from multiple projects within the same organization.

---

## Feature: Comments
**Status**: 🟢 8/8 requirements implemented (100%)
**Detail Spec**: [detailed/comments_detailed_spec.md](detailed/comments_detailed_spec.md)
**Purpose**: Discussion and collaboration on tickets
**Version**: V1

### Rationale
Users need to discuss tickets, provide updates, and collaborate. Comments allow threaded discussion on tickets. No attachments in V1.

### High-Level Requirements
- ✅ REQ-COMMENT-001: Add comment to ticket
- ✅ REQ-COMMENT-002: Retrieve comment by ID
- ✅ REQ-COMMENT-003: List comments for ticket
- ✅ REQ-COMMENT-004: Update comment (by author)
- ✅ REQ-COMMENT-005: Delete comment (by author or admin)
- ✅ REQ-COMMENT-006: Comments include author and timestamp
- ✅ REQ-COMMENT-007: Comments are organization-scoped
- ✅ REQ-COMMENT-008: Handle validation and permission errors

**Notes**: Complete comment functionality with 5 REST endpoints. Write Access+ users can create comments; all users can read comments in their organization. Author-only editing (even admins cannot edit others' comments). Author or Admin can delete comments. Content limited to 5000 chars. Chronological ordering (oldest first) for discussion flow. Activity logging for all CUD operations. 28 comprehensive API tests + 15 repository tests.

---

## Feature: Activity Logs & Audit Trails
**Status**: 🟢 7/7 requirements implemented (100%) - V1 Complete
**Detail Spec**: [detailed/activity_logs_detailed_spec.md](detailed/activity_logs_detailed_spec.md)
**Purpose**: Track changes and provide audit trail
**Version**: V1

### Rationale
For compliance and transparency, the system tracks all changes to tickets, projects, and other entities. Users can view activity logs based on their permissions.

### High-Level Requirements
- ✅ REQ-ACTIVITY-001: Log all ticket changes
- ✅ REQ-ACTIVITY-002: Log project changes
- ✅ REQ-ACTIVITY-003: Log user actions (create, update, delete)
- ✅ REQ-ACTIVITY-004: Retrieve activity log for entity
- ✅ REQ-ACTIVITY-005: Filter activity logs by date, user, action type
- ✅ REQ-ACTIVITY-006: Activity logs respect user permissions (users only see logs for data they can access)
- ✅ REQ-ACTIVITY-007: Activity logs are immutable (cannot be modified/deleted)

**Notes**: Complete activity logging with 100% coverage across all mutation operations: 6 ticket operations, 5 project operations, 3 user operations (create, update, delete), plus password changes. Sensitive data properly redacted (passwords never logged). Query API provides comprehensive filtering (entity type, entity ID, actor, action, date range, organization) with permission-based access control. Super Admin sees all logs; other roles see only their organization's logs. Logs are read-only (no POST/PUT/DELETE endpoints). 13 API tests + 21 repository tests + 4 user activity tests verify all scenarios.

---

## Feature: Custom Workflows
**Status**: ✅ 10/10 requirements implemented (100%)
**Detail Spec**: [detailed/workflows_detailed_spec.md](detailed/workflows_detailed_spec.md)
**Purpose**: Allow organizations to define custom ticket workflows
**Version**: V2

### Rationale
Different teams have different processes. While TODO/IN_PROGRESS/DONE works for many, others need custom statuses that match their specific workflows (e.g., "BACKLOG", "CODE_REVIEW", "QA", "DEPLOYED" or "NEW", "TRIAGED", "ASSIGNED", "RESOLVED", "CLOSED").

### High-Level Requirements
- ✅ REQ-WORKFLOW-001: Create workflow with custom statuses
- ✅ REQ-WORKFLOW-002: Retrieve workflow by ID
- ✅ REQ-WORKFLOW-003: List workflows in organization
- ✅ REQ-WORKFLOW-004: Update workflow details
- ✅ REQ-WORKFLOW-005: Delete workflow (if not in use)
- ✅ REQ-WORKFLOW-006: Default workflow exists for each organization
- ✅ REQ-WORKFLOW-007: Workflow validation (status format, uniqueness)
- ✅ REQ-WORKFLOW-008: Organization scoping for workflows
- ✅ REQ-WORKFLOW-009: Cannot update workflow if it breaks existing tickets
- ✅ REQ-WORKFLOW-010: Handle not-found and permission errors

**Notes**: Workflows are organization-scoped. Each org has a default workflow (TODO/IN_PROGRESS/DONE) for backward compatibility. Projects can choose a workflow; tickets must have statuses valid for their project's workflow. V1 allows all status transitions; future versions may add transition constraints.

---

## Future Features (Not Yet Planned)

### Custom Fields
**Version**: V2
- Define custom fields on tickets
- Field types (text, number, date, dropdown, etc.)
- Field validation rules

### Attachments
**Version**: V2
- Upload files to tickets/comments
- File storage and retrieval
- File access permissions

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
