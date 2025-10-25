"""Domain business data models for the project management application.

This module contains Pydantic models for representing the domain, API data validation and serialization.

The StubEntity models serve as a template/scaffolding for creating real domain entities.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StubEntityData(BaseModel):
    """Base data structure for stub entity - template for creating real entities."""

    name: str = Field(..., min_length=1, max_length=255, description="Stub entity name")
    description: Optional[str] = Field(None, max_length=1000, description="Stub entity description")


class StubEntity(StubEntityData):
    """Complete stub entity with metadata - template for creating real entities."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Stub entity ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class StubEntityCreateCommand(BaseModel):
    """Command model for creating a new stub entity - template for real create commands."""

    stub_entity_data: StubEntityData


class StubEntityUpdateCommand(BaseModel):
    """Command model for updating an existing stub entity - template for real update commands."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Stub entity name")
    description: Optional[str] = Field(None, max_length=1000, description="Stub entity description")


# Organization Models


class OrganizationData(BaseModel):
    """Base organization data structure."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Organization name (must be unique)",
    )
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")


class Organization(OrganizationData):
    """Complete organization model with metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Organization ID")
    is_active: bool = Field(True, description="Whether organization is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class OrganizationCreateCommand(BaseModel):
    """Command model for creating a new organization."""

    organization_data: OrganizationData


class OrganizationUpdateCommand(BaseModel):
    """Command model for updating an existing organization."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")
    is_active: Optional[bool] = Field(None, description="Whether organization is active")


# Project Models


class ProjectData(BaseModel):
    """Base project data structure."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Project name",
    )
    description: Optional[str] = Field(None, max_length=1000, description="Project description")


class Project(ProjectData):
    """Complete project model with metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Project ID")
    organization_id: str = Field(..., description="Organization ID this project belongs to")
    is_active: bool = Field(True, description="Whether project is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProjectCreateCommand(BaseModel):
    """Command model for creating a new project."""

    project_data: ProjectData
    organization_id: str = Field(..., description="Organization ID this project belongs to")


class ProjectUpdateCommand(BaseModel):
    """Command model for updating an existing project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    is_active: Optional[bool] = Field(None, description="Whether project is active")


# Ticket Models


class TicketStatus(str, Enum):
    """Ticket status workflow states."""

    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TicketPriority(str, Enum):
    """Ticket priority levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketData(BaseModel):
    """Base ticket data structure."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Ticket title",
    )
    description: Optional[str] = Field(None, max_length=2000, description="Ticket description")
    priority: Optional[TicketPriority] = Field(None, description="Ticket priority level")


class Ticket(TicketData):
    """Complete ticket model with metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Ticket ID")
    status: TicketStatus = Field(..., description="Ticket status")
    assignee_id: Optional[str] = Field(None, description="ID of user assigned to this ticket")
    reporter_id: str = Field(..., description="ID of user who created this ticket")
    project_id: str = Field(..., description="Project ID this ticket belongs to")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TicketCreateCommand(BaseModel):
    """Command model for creating a new ticket."""

    ticket_data: TicketData
    project_id: str = Field(..., description="Project ID this ticket belongs to")
    assignee_id: Optional[str] = Field(None, description="ID of user to assign to this ticket")


class TicketUpdateCommand(BaseModel):
    """Command model for updating an existing ticket."""

    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Ticket title")
    description: Optional[str] = Field(None, max_length=2000, description="Ticket description")
    priority: Optional[TicketPriority] = Field(None, description="Ticket priority level")


# User Management Models


class UserRole(str, Enum):
    """User roles for role-based access control."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"
    WRITE_ACCESS = "write_access"
    READ_ACCESS = "read_access"


class UserData(BaseModel):
    """Base user data structure."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username (alphanumeric, underscore, dash only)",
    )
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User full name")


class User(UserData):
    """Complete user model with metadata."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User ID")
    organization_id: Optional[str] = Field(None, description="Organization ID (None for Super Admin)")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(True, description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserAuthData(BaseModel):
    """User authentication data including password hash.

    This model is used exclusively for authentication purposes where password
    verification is required. It should NEVER be exposed outside the authentication
    layer.

    Note: This is a domain model, not an ORM model. Repository methods must return
    this domain model, never ORM objects.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    password_hash: str = Field(..., description="Hashed password for verification")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    role: UserRole = Field(..., description="User role")
    is_active: bool = Field(..., description="Whether user is active")


class UserCreateCommand(BaseModel):
    """Command model for creating a new user."""

    user_data: UserData
    password: str = Field(..., min_length=1, description="Plain text password (will be hashed)")
    organization_id: Optional[str] = Field(None, description="Organization ID (None for Super Admin)")
    role: UserRole = Field(..., description="User role")


class UserUpdateCommand(BaseModel):
    """Command model for updating an existing user.

    Only specified fields will be updated. username, organization_id, and password
    cannot be changed via this command.
    """

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether user is active")


class UserCreateResponse(BaseModel):
    """Response model for user creation including generated password.

    The generated_password is ONLY returned on creation and cannot be retrieved later.
    """

    user: User = Field(..., description="Created user details")
    generated_password: str = Field(..., description="Generated password (returned only once)")


# Authentication models


class LoginRequest(BaseModel):
    """Login request with username and password."""

    username: str = Field(..., min_length=1, description="Username (case-insensitive)")
    password: str = Field(..., min_length=1, description="Password (case-sensitive)")


class LoginResponse(BaseModel):
    """Successful login response with token and user info."""

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field("bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token lifetime in seconds")
    user_id: str = Field(..., description="ID of authenticated user")
    organization_id: Optional[str] = Field(None, description="User's organization ID")
    role: UserRole = Field(..., description="User's current role")


class ChangePasswordRequest(BaseModel):
    """Request to change user's password."""

    current_password: str = Field(..., min_length=1, description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (must meet strength requirements)")
