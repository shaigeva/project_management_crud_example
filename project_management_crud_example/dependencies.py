"""Shared dependency injection functions for FastAPI.

This module provides shared dependency functions that can be used across
the application and routers without creating circular imports.
"""

from typing import Iterator, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import Repository, StubEntityRepository
from project_management_crud_example.domain_models import User
from project_management_crud_example.exceptions import (
    AccountInactiveException,
    AuthenticationRequiredException,
    InvalidTokenError,
    InvalidTokenException,
    TokenExpiredError,
    TokenExpiredException,
)
from project_management_crud_example.utils.jwt import decode_access_token

# Global database instance
_db_instance: Database | None = None


def get_database(db_path: str = "stub_entities.db") -> Database:
    """Get or create the database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def get_db_session() -> Iterator[Session]:
    """Dependency to get database session."""
    db = get_database()
    with db.get_session() as session:
        yield session


def get_repository(session: Session = Depends(get_db_session)) -> Repository:  # noqa: B008
    """Dependency to get the main repository instance."""
    return Repository(session)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    repo: Repository = Depends(get_repository),  # noqa: B008
) -> User:
    """Extract and validate user from Bearer token.

    Args:
        authorization: Authorization header value (format: "Bearer <token>")
        repo: Repository instance for database access

    Returns:
        User domain model with current role and is_active status

    Raises:
        AuthenticationRequiredException: No authorization header provided
        InvalidTokenException: Token is malformed or invalid
        TokenExpiredException: Token has expired
        AccountInactiveException: User account is inactive

    Note:
        - User role is fetched from database on every request
        - This ensures immediate effect of permission changes and user deactivation
    """
    # Check if authorization header is provided
    if not authorization:
        raise AuthenticationRequiredException()

    # Validate authorization header format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenException()

    token = parts[1]

    # Decode and validate token
    try:
        claims = decode_access_token(token)
    except TokenExpiredError:
        raise TokenExpiredException() from None
    except InvalidTokenError:
        raise InvalidTokenException() from None

    # Fetch user from database to get current role and is_active status
    user = repo.users.get_by_id(claims.user_id)
    if not user:
        raise InvalidTokenException()

    # Check if user is active
    if not user.is_active:
        raise AccountInactiveException()

    return user


def get_stub_entity_repo(session: Session = Depends(get_db_session)) -> StubEntityRepository:  # noqa: B008
    """Dependency to get stub entity repository - template for creating real repository dependencies."""
    return StubEntityRepository(session)
