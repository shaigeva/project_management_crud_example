"""Ticket API endpoints.

This module provides ticket CRUD endpoints with role-based permissions and organization scoping.
Tickets belong to projects, and access is controlled through project organization membership.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.dependencies import get_current_user, get_repository
from project_management_crud_example.domain_models import (
    ActionType,
    ActivityLogCreateCommand,
    Ticket,
    TicketCreateCommand,
    TicketData,
    TicketStatus,
    TicketUpdateCommand,
    User,
    UserRole,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


# Request/Response models for specialized endpoints
class TicketStatusUpdate(BaseModel):
    """Request model for updating ticket status."""

    status: TicketStatus


class TicketProjectUpdate(BaseModel):
    """Request model for moving ticket to different project."""

    project_id: str


class TicketAssigneeUpdate(BaseModel):
    """Request model for assigning/unassigning ticket."""

    assignee_id: Optional[str] = None


def _get_project_and_check_access(
    project_id: str,
    repo: Repository,
    current_user: User,
    operation: str,
) -> None:
    """Get project and verify user has access to it.

    Args:
        project_id: ID of project to check
        repo: Repository instance
        current_user: Current authenticated user
        operation: Description of operation for logging

    Raises:
        HTTP 404: Project not found
        HTTP 403: User attempting to access project in different organization
    """
    project = repo.projects.get_by_id(project_id)

    if not project:
        logger.debug(f"Project not found: {project_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Permission check: Super Admin can access any, others only their own org
    if current_user.role != UserRole.SUPER_ADMIN:
        if project.organization_id != current_user.organization_id:
            logger.warning(
                f"User {current_user.id} attempted to {operation} in project {project_id} from different org"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: project belongs to different organization",
            )


def _get_ticket_and_check_access(
    ticket_id: str,
    repo: Repository,
    current_user: User,
    operation: str,
) -> Ticket:
    """Get ticket and verify user has access to it (via project organization).

    Args:
        ticket_id: ID of ticket to check
        repo: Repository instance
        current_user: Current authenticated user
        operation: Description of operation for logging

    Returns:
        Ticket if found and accessible

    Raises:
        HTTP 404: Ticket not found
        HTTP 403: User attempting to access ticket in different organization
    """
    ticket = repo.tickets.get_by_id(ticket_id)

    if not ticket:
        logger.debug(f"Ticket not found: {ticket_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    # Check project access (tickets inherit access from their project)
    _get_project_and_check_access(ticket.project_id, repo, current_user, operation)

    return ticket


def _log_ticket_activity(
    repo: Repository,
    ticket: Ticket,
    action: ActionType,
    actor_id: str,
    changes: dict,
) -> None:
    """Create activity log entry for ticket operation.

    Args:
        repo: Repository instance
        ticket: Ticket that was operated on
        action: Type of action performed
        actor_id: User who performed the action
        changes: Dict describing what changed

    Note: Failures to log are caught and logged but don't fail the operation.
    """
    try:
        # Get organization from project
        project = repo.projects.get_by_id(ticket.project_id)
        if not project:
            logger.warning(f"Cannot log activity: project {ticket.project_id} not found")
            return

        command = ActivityLogCreateCommand(
            entity_type="ticket",
            entity_id=ticket.id,
            action=action,
            actor_id=actor_id,
            organization_id=project.organization_id,
            changes=changes,
        )
        repo.activity_logs.create(command)
        logger.debug(f"Activity logged: {action.value} for ticket {ticket.id}")
    except Exception as e:
        # Don't fail the operation if logging fails
        logger.error(f"Failed to log ticket activity: {e}", exc_info=True)


@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketData,
    project_id: str = Query(..., description="Project ID this ticket belongs to"),
    assignee_id: Optional[str] = Query(None, description="Optional user ID to assign ticket to"),
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Create a new ticket in a project.

    Permission rules:
    - Admin/Project Manager/Write users: Can create tickets in their org's projects
    - Read users: Cannot create tickets
    - Reporter is automatically set to current user

    Args:
        ticket_data: Ticket data (title, description, priority)
        project_id: ID of project to create ticket in
        assignee_id: Optional user ID to assign ticket to
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Created Ticket with id, status=TODO, and timestamps

    Raises:
        HTTP 403: User does not have permission to create tickets
        HTTP 404: Project or assignee not found
        HTTP 400: Project in different organization
    """
    # Permission check: Only Admin, PM, and Write users can create tickets
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.WRITE_ACCESS}
    if current_user.role not in allowed_roles:
        logger.warning(f"User {current_user.id} ({current_user.role}) attempted to create ticket without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create tickets",
        )

    # Verify project exists and user has access to it
    _get_project_and_check_access(project_id, repo, current_user, "create ticket")

    # If assignee specified, verify user exists and is in same organization
    if assignee_id:
        assignee = repo.users.get_by_id(assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found",
            )

        # Check assignee is active
        if not assignee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign to inactive user",
            )

        # Check assignee in same organization (Super Admin can assign cross-org)
        if current_user.role != UserRole.SUPER_ADMIN:
            if assignee.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot assign to user in different organization",
                )

    logger.info(f"Creating ticket: {ticket_data.title} in project {project_id} (by user {current_user.id})")

    command = TicketCreateCommand(
        ticket_data=ticket_data,
        project_id=project_id,
        assignee_id=assignee_id,
    )

    ticket = repo.tickets.create(command, reporter_id=current_user.id)
    logger.info(f"Ticket created: {ticket.id}")

    # Log activity
    _log_ticket_activity(
        repo=repo,
        ticket=ticket,
        action=ActionType.TICKET_CREATED,
        actor_id=current_user.id,
        changes={
            "created": {
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value,
                "priority": ticket.priority.value if ticket.priority else None,
                "assignee_id": ticket.assignee_id,
                "reporter_id": ticket.reporter_id,
                "project_id": ticket.project_id,
            }
        },
    )

    return ticket


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Get ticket by ID.

    Permission rules:
    - Super Admin: Can access any ticket
    - Other users: Can only access tickets from their org's projects

    Args:
        ticket_id: ID of ticket to retrieve
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Ticket if found and user has permission

    Raises:
        HTTP 403: User attempting to access ticket in different organization
        HTTP 404: Ticket not found
    """
    logger.debug(f"Getting ticket: {ticket_id} (by user {current_user.id})")

    ticket = _get_ticket_and_check_access(ticket_id, repo, current_user, "view ticket")

    return ticket


@router.get("", response_model=List[Ticket])
async def list_tickets(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),  # noqa: B008
    status: Optional[TicketStatus] = Query(None, description="Filter by status"),  # noqa: B008
    assignee_id: Optional[str] = Query(None, description="Filter by assignee user ID"),  # noqa: B008
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> List[Ticket]:
    """List tickets with optional filtering.

    Permission rules:
    - Super Admin: Can see all tickets across all organizations
    - Other users: Can only see tickets from their org's projects

    Args:
        project_id: Optional filter by project ID
        status: Optional filter by ticket status
        assignee_id: Optional filter by assignee
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        List of tickets the user has permission to access
    """
    logger.debug(
        f"Listing tickets (by user {current_user.id}, filters: project={project_id}, status={status}, assignee={assignee_id})"
    )

    # If Super Admin, return all tickets (with optional filters)
    if current_user.role == UserRole.SUPER_ADMIN:
        return repo.tickets.get_by_filters(
            project_id=project_id,
            status=status,
            assignee_id=assignee_id,
        )

    # For non-Super Admin, need to filter to user's organization
    # Get all projects in user's organization
    user_org_projects = repo.projects.get_by_organization_id(current_user.organization_id)  # type: ignore[arg-type]
    user_project_ids = {p.id for p in user_org_projects}

    # If project_id filter specified, verify it's in user's org
    if project_id:
        if project_id not in user_project_ids:
            # Project doesn't exist in user's org - return empty list
            logger.debug(f"User {current_user.id} filtering by project {project_id} not in their org")
            return []

        # Get tickets for the specific project with other filters
        return repo.tickets.get_by_filters(
            project_id=project_id,
            status=status,
            assignee_id=assignee_id,
        )

    # No project_id filter - get all tickets from user's org projects
    all_org_tickets: List[Ticket] = []
    for proj_id in user_project_ids:
        tickets = repo.tickets.get_by_filters(
            project_id=proj_id,
            status=status,
            assignee_id=assignee_id,
        )
        all_org_tickets.extend(tickets)

    # Sort by created_at (most recent first)
    all_org_tickets.sort(key=lambda t: t.created_at, reverse=True)

    return all_org_tickets


@router.put("/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: str,
    update_data: TicketUpdateCommand,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Update ticket fields (title, description, priority).

    Permission rules:
    - Admin/Project Manager/Write users: Can update tickets in their org's projects
    - Read users: Cannot update tickets

    Args:
        ticket_id: ID of ticket to update
        update_data: Fields to update
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Updated ticket

    Raises:
        HTTP 403: User does not have permission to update tickets
        HTTP 404: Ticket not found
        HTTP 422: Validation error
    """
    # Permission check: Only Admin, PM, and Write users can update tickets
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.WRITE_ACCESS}
    if current_user.role not in allowed_roles:
        logger.warning(f"User {current_user.id} ({current_user.role}) attempted to update ticket without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update tickets",
        )

    # Verify ticket exists and user has access
    old_ticket = _get_ticket_and_check_access(ticket_id, repo, current_user, "update ticket")

    logger.info(f"Updating ticket: {ticket_id} (by user {current_user.id})")

    updated_ticket = repo.tickets.update(ticket_id, update_data)

    if not updated_ticket:
        # Shouldn't happen since we verified existence above
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    logger.info(f"Ticket updated: {ticket_id}")

    # Log activity - capture what changed
    changes = {}
    if updated_ticket.title != old_ticket.title:
        changes["title"] = {"old_value": old_ticket.title, "new_value": updated_ticket.title}
    if updated_ticket.description != old_ticket.description:
        changes["description"] = {"old_value": old_ticket.description, "new_value": updated_ticket.description}
    if updated_ticket.priority != old_ticket.priority:
        changes["priority"] = {
            "old_value": old_ticket.priority.value if old_ticket.priority else None,
            "new_value": updated_ticket.priority.value if updated_ticket.priority else None,
        }

    if changes:  # Only log if something actually changed
        _log_ticket_activity(
            repo=repo,
            ticket=updated_ticket,
            action=ActionType.TICKET_UPDATED,
            actor_id=current_user.id,
            changes=changes,
        )

    return updated_ticket


@router.put("/{ticket_id}/status", response_model=Ticket)
async def update_ticket_status(
    ticket_id: str,
    status_update: TicketStatusUpdate,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Change ticket status (workflow transition).

    Permission rules:
    - Admin/Project Manager/Write users: Can change status in their org's projects
    - Read users: Cannot change status

    Args:
        ticket_id: ID of ticket to update
        status_update: New status
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Updated ticket

    Raises:
        HTTP 403: User does not have permission to change ticket status
        HTTP 404: Ticket not found
    """
    # Permission check: Only Admin, PM, and Write users can change status
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.WRITE_ACCESS}
    if current_user.role not in allowed_roles:
        logger.warning(
            f"User {current_user.id} ({current_user.role}) attempted to change ticket status without permission"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to change ticket status",
        )

    # Verify ticket exists and user has access
    old_ticket = _get_ticket_and_check_access(ticket_id, repo, current_user, "change ticket status")

    logger.info(f"Changing ticket status: {ticket_id} to {status_update.status.value} (by user {current_user.id})")

    updated_ticket = repo.tickets.update_status(ticket_id, status_update.status)

    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    logger.info(f"Ticket status updated: {ticket_id}")

    # Log activity
    _log_ticket_activity(
        repo=repo,
        ticket=updated_ticket,
        action=ActionType.TICKET_STATUS_CHANGED,
        actor_id=current_user.id,
        changes={"status": {"old_value": old_ticket.status.value, "new_value": updated_ticket.status.value}},
    )

    return updated_ticket


@router.put("/{ticket_id}/project", response_model=Ticket)
async def move_ticket_to_project(
    ticket_id: str,
    project_update: TicketProjectUpdate,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Move ticket to a different project.

    Permission rules:
    - Admin/Project Manager: Can move tickets between projects in their org
    - Write/Read users: Cannot move tickets

    Args:
        ticket_id: ID of ticket to move
        project_update: Target project ID
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Updated ticket

    Raises:
        HTTP 403: User does not have permission or projects in different orgs
        HTTP 404: Ticket or target project not found
    """
    # Permission check: Only Admin and PM can move tickets
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER}
    if current_user.role not in allowed_roles:
        logger.warning(f"User {current_user.id} ({current_user.role}) attempted to move ticket without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to move tickets",
        )

    # Verify ticket exists and user has access to source project
    old_ticket = _get_ticket_and_check_access(ticket_id, repo, current_user, "move ticket")

    # Verify target project exists and user has access to it
    _get_project_and_check_access(project_update.project_id, repo, current_user, "move ticket to project")

    # Both projects verified to be in user's org (or user is Super Admin)

    logger.info(
        f"Moving ticket {ticket_id} from project {old_ticket.project_id} to {project_update.project_id} (by user {current_user.id})"
    )

    updated_ticket = repo.tickets.update_project(ticket_id, project_update.project_id)

    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    logger.info(f"Ticket moved: {ticket_id}")

    # Log activity
    _log_ticket_activity(
        repo=repo,
        ticket=updated_ticket,
        action=ActionType.TICKET_MOVED,
        actor_id=current_user.id,
        changes={"project_id": {"old_value": old_ticket.project_id, "new_value": updated_ticket.project_id}},
    )

    return updated_ticket


@router.put("/{ticket_id}/assignee", response_model=Ticket)
async def update_ticket_assignee(
    ticket_id: str,
    assignee_update: TicketAssigneeUpdate,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Ticket:
    """Assign or unassign ticket to a user.

    Permission rules:
    - Admin/Project Manager: Can assign tickets in their org's projects
    - Write/Read users: Cannot assign tickets

    Args:
        ticket_id: ID of ticket to assign
        assignee_update: User ID to assign (or null to unassign)
        repo: Repository instance for database access
        current_user: Current authenticated user

    Returns:
        Updated ticket

    Raises:
        HTTP 403: User does not have permission or assignee in different org
        HTTP 404: Ticket or assignee user not found
        HTTP 400: Assignee user is inactive
    """
    # Permission check: Only Admin and PM can assign tickets
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PROJECT_MANAGER}
    if current_user.role not in allowed_roles:
        logger.warning(f"User {current_user.id} ({current_user.role}) attempted to assign ticket without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to assign tickets",
        )

    # Verify ticket exists and user has access
    old_ticket = _get_ticket_and_check_access(ticket_id, repo, current_user, "assign ticket")

    # If assigning (not unassigning), verify assignee exists and is valid
    if assignee_update.assignee_id:
        assignee = repo.users.get_by_id(assignee_update.assignee_id)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found",
            )

        # Check assignee is active
        if not assignee.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign to inactive user",
            )

        # Check assignee in same organization (Super Admin can assign cross-org)
        if current_user.role != UserRole.SUPER_ADMIN:
            if assignee.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot assign to user in different organization",
                )

    logger.info(f"Assigning ticket {ticket_id} to {assignee_update.assignee_id} (by user {current_user.id})")

    updated_ticket = repo.tickets.update_assignee(ticket_id, assignee_update.assignee_id)

    if not updated_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    logger.info(f"Ticket assignee updated: {ticket_id}")

    # Log activity
    _log_ticket_activity(
        repo=repo,
        ticket=updated_ticket,
        action=ActionType.TICKET_ASSIGNED,
        actor_id=current_user.id,
        changes={"assignee_id": {"old_value": old_ticket.assignee_id, "new_value": updated_ticket.assignee_id}},
    )

    return updated_ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: str,
    repo: Repository = Depends(get_repository),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> None:
    """Delete a ticket.

    Permission rules:
    - Admin only: Can delete tickets in their org's projects
    - Other roles: Cannot delete tickets

    Args:
        ticket_id: ID of ticket to delete
        repo: Repository instance for database access
        current_user: Current authenticated user

    Raises:
        HTTP 403: User does not have permission to delete tickets
        HTTP 404: Ticket not found
    """
    # Permission check: Only Admin can delete tickets
    allowed_roles = {UserRole.SUPER_ADMIN, UserRole.ADMIN}
    if current_user.role not in allowed_roles:
        logger.warning(f"User {current_user.id} ({current_user.role}) attempted to delete ticket without permission")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete tickets",
        )

    # Verify ticket exists and user has access - capture snapshot before deletion
    ticket_snapshot = _get_ticket_and_check_access(ticket_id, repo, current_user, "delete ticket")

    logger.info(f"Deleting ticket: {ticket_id} (by user {current_user.id})")

    success = repo.tickets.delete(ticket_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    logger.info(f"Ticket deleted: {ticket_id}")

    # Log activity - include snapshot of deleted ticket
    _log_ticket_activity(
        repo=repo,
        ticket=ticket_snapshot,
        action=ActionType.TICKET_DELETED,
        actor_id=current_user.id,
        changes={
            "deleted": {
                "id": ticket_snapshot.id,
                "title": ticket_snapshot.title,
                "description": ticket_snapshot.description,
                "status": ticket_snapshot.status.value,
                "priority": ticket_snapshot.priority.value if ticket_snapshot.priority else None,
                "assignee_id": ticket_snapshot.assignee_id,
                "reporter_id": ticket_snapshot.reporter_id,
                "project_id": ticket_snapshot.project_id,
            }
        },
    )
