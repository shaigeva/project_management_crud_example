# Comments: Detailed Specification

**Status**: 🔴 0/8 requirements implemented (0%)
**Parent**: [Main Spec](../main_spec.md#feature-comments)
**Last Updated**: 2025-01-26

## Rationale

Comments enable collaboration and discussion on tickets. Users need to:
- Add comments to provide updates, ask questions, share information
- View comment history on tickets to understand context
- Edit their own comments to fix typos or clarify
- Remove inappropriate or outdated comments
- Track who said what and when

This spec defines the **externally observable behavior** of comment functionality, focusing on what users can verify through the API.

---

## REQ-COMMENT-001: Add comment to ticket
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user adds a comment to a ticket they have access to

### Observable Behavior
User can post a comment on a ticket via API and subsequently retrieve it to verify it was created correctly.

### Acceptance Criteria
- POST /tickets/{ticket_id}/comments with valid content returns 201 response
- Response contains created comment with all fields:
  - `id`: Unique identifier (non-empty string)
  - `ticket_id`: ID of the ticket this comment belongs to
  - `author_id`: ID of user who created the comment (automatically set to current user)
  - `content`: The comment text provided by user
  - `created_at`: Timestamp when comment was created
  - `updated_at`: Timestamp of last update (same as created_at initially)
- After creation, GET /comments/{id} returns the same comment
- After creation, GET /tickets/{ticket_id}/comments includes the new comment
- Content is required (non-empty string)
- Content has reasonable length limit (max 5000 characters)
- Author is automatically set to authenticated user (cannot be specified in request)
- Users can only comment on tickets from projects in their organization
- Commenting on non-existent ticket returns 404
- Commenting on ticket in different organization returns 403

### Edge Cases
- Maximum length content (5000 characters)
- Minimum length content (1 character)
- Special characters in content
- Unicode characters in content (日本語, Español, emoji 😀)
- Multiple line breaks and whitespace
- Attempting to comment on ticket from different organization
- Attempting to comment on non-existent ticket

---

## REQ-COMMENT-002: Retrieve comment by ID
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests a specific comment by its ID

### Observable Behavior
User can retrieve a specific comment by ID or receive appropriate error if not found or unauthorized.

### Acceptance Criteria
- GET /comments/{id} for existing comment returns 200 with comment data
- Returned data matches what was stored during creation
- Response includes all comment fields (id, ticket_id, author_id, content, timestamps)
- GET /comments/{id} for non-existent ID returns 404
- GET /comments/{id} for comment on ticket in different organization returns 403
- 404 response includes error message/detail field
- Multiple GET requests for same ID return consistent data

### Edge Cases
- Non-existent comment IDs
- Comments on tickets from different organizations
- Deleted comments

---

## REQ-COMMENT-003: List comments for ticket
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user requests all comments for a specific ticket

### Observable Behavior
User can retrieve all comments for a ticket they have access to, ordered chronologically.

### Acceptance Criteria
- GET /tickets/{ticket_id}/comments returns 200 with array of comments
- If no comments exist, returns empty array []
- Comments are ordered by created_at (oldest first, chronological discussion order)
- Each comment has same structure as individual GET response
- All comments on the ticket appear in the list
- Deleted comments do not appear in the list
- Users can only list comments for tickets in their organization
- Listing comments for non-existent ticket returns 404
- Listing comments for ticket in different organization returns 403

### Edge Cases
- Ticket with no comments (empty array)
- Ticket with many comments
- Comments from different users
- Comments with various content lengths

---

## REQ-COMMENT-004: Update comment (by author)
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user updates the content of their own comment

### Observable Behavior
Comment author can edit their comment content; others cannot.

### Acceptance Criteria
- PUT /comments/{id} with new content returns 200 with updated comment
- Response contains comment with new content
- updated_at timestamp is updated to current time
- created_at timestamp remains unchanged
- Only the comment author can update their comment
- Non-author attempting to update returns 403
- Admin cannot update other users' comments (comments are owned by author)
- Cannot update id, ticket_id, author_id, or created_at
- Updated content must meet same validation as creation (non-empty, max 5000 chars)
- Updating non-existent comment returns 404
- Updating comment on ticket in different organization returns 403
- Subsequent GET shows updated content

### Edge Cases
- Author updating their own comment succeeds
- Non-author attempting to update returns 403
- Admin attempting to update other's comment returns 403 (deliberate design choice)
- Empty content returns 422 validation error
- Content exceeding max length returns 422 validation error
- Partial updates (only content field can be updated)

---

## REQ-COMMENT-005: Delete comment (by author or admin)
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When a user deletes a comment

### Observable Behavior
Comment author or organization Admin can delete comments; others cannot.

### Acceptance Criteria
- DELETE /comments/{id} returns 204 (no content)
- After deletion, GET /comments/{id} returns 404
- Deleted comment does not appear in ticket's comment list
- Comment author can delete their own comment
- Admin (organization Admin or Super Admin) can delete any comment in their organization
- Super Admin can delete any comment in any organization
- Project Manager and Write Access users cannot delete others' comments
- Non-author/non-admin attempting to delete returns 403
- Deleting non-existent comment returns 404
- Deleting comment on ticket in different organization returns 403

### Edge Cases
- Author deleting their own comment succeeds
- Admin deleting any comment in their org succeeds
- Super Admin deleting comment in any org succeeds
- Project Manager deleting other's comment returns 403
- Write Access user deleting other's comment returns 403
- Non-author/non-admin attempting to delete returns 403
- Deleting non-existent comment returns 404

---

## REQ-COMMENT-006: Comments include author and timestamp
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When working with comments, metadata about authorship and timing is available

### Observable Behavior
Every comment includes information about who wrote it and when.

### Acceptance Criteria
- Every comment has: id, ticket_id, author_id, content, created_at, updated_at
- author_id references the user who created the comment
- author_id is automatically set to current user (cannot be specified)
- created_at is set when comment is created
- updated_at is set to created_at initially
- updated_at is updated when comment content is changed
- Timestamps are ISO format with timezone
- id is unique across all comments

### Edge Cases
- created_at never changes after creation
- updated_at changes with every edit
- author_id never changes (comments are permanently owned by creator)

---

## REQ-COMMENT-007: Comments are organization-scoped
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When accessing comments across organizations

### Observable Behavior
Users can only access comments on tickets from their organization. Comments inherit organization scope from their ticket.

### Acceptance Criteria
- Users cannot see comments on tickets from other organizations
- Super Admin can see all comments on all tickets
- Attempting to access comment from different org returns 403
- Creating comment on ticket from different org returns 403
- Updating comment on ticket from different org returns 403
- Deleting comment on ticket from different org returns 403
- List operations only return comments from tickets in user's organization

### Edge Cases
- Cross-organization access attempts (all return 403)
- Super Admin access to all organizations
- Admin can only manage comments in their own organization

---

## REQ-COMMENT-008: Handle validation and permission errors
**Status**: 🔴 Not Implemented
**Type**: Product Behavior

### Scenario
When providing invalid data or attempting unauthorized actions

### Observable Behavior
Clear error messages for validation failures and permission denials.

### Acceptance Criteria
- POST /tickets/{ticket_id}/comments with empty content returns 422
- POST with content exceeding 5000 chars returns 422
- PUT /comments/{id} with empty content returns 422
- PUT with content exceeding 5000 chars returns 422
- Error messages identify which field is invalid
- Non-author updating comment returns 403 with clear message
- Non-admin/non-author deleting comment returns 403 with clear message
- Accessing comment from different org returns 403
- Accessing non-existent comment returns 404 with "Comment not found"
- Commenting on non-existent ticket returns 404 with "Ticket not found"

### Edge Cases
- Empty content (required field)
- Content too long (>5000 characters)
- Permission denied scenarios (403)
- Resource not found scenarios (404)
- Invalid data types

---

## Implementation Notes

### Data Model
- Comment entity with fields: id, ticket_id, author_id, content, created_at, updated_at
- Foreign key relationship to Ticket
- Foreign key relationship to User (author)
- Organization scope inherited from Ticket's Project

### Authorization Rules
- **Create**: Any user with write access or higher in the ticket's organization
- **Read**: Any user with access to the ticket (same org or Super Admin)
- **Update**: Only the comment author
- **Delete**: Comment author OR Admin/Super Admin

### No Nested Comments in V1
- V1 supports flat comments only (all comments are direct replies to ticket)
- No parent/child relationships between comments
- No threading or reply functionality
- Future versions may add comment threading

### No Attachments in V1
- V1 supports text-only comments
- No file attachments or media
- Future versions may add attachment support

---

## API Endpoints Summary

| Method | Endpoint | Description | Auth Level |
|--------|----------|-------------|------------|
| POST | /tickets/{ticket_id}/comments | Create comment | Write Access+ |
| GET | /comments/{id} | Get comment by ID | Read Access+ |
| GET | /tickets/{ticket_id}/comments | List ticket comments | Read Access+ |
| PUT | /comments/{id} | Update comment | Author only |
| DELETE | /comments/{id} | Delete comment | Author or Admin |
