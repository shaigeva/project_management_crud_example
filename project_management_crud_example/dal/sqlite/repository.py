"""Repository classes for data access operations.

This module provides a single Repository class that handles all database operations
for the project management application, following the Repository pattern to
separate business logic from data access logic.

The Repository class uses nested classes for organization (e.g., repo.users, repo.organizations).
This allows for clean organization while enabling cross-entity queries naturally.

The StubEntities nested class serves as a template/scaffolding for reference.
"""

import logging
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from project_management_crud_example.domain_models import (
    StubEntity,
    StubEntityCreateCommand,
    StubEntityUpdateCommand,
    User,
    UserAuthData,
    UserCreateCommand,
)
from project_management_crud_example.utils.password import generate_password, hash_password

from .converters import (
    orm_stub_entities_to_business_stub_entities,
    orm_stub_entity_to_business_stub_entity,
    orm_user_to_domain_user,
    orm_user_to_user_auth_data,
)
from .orm_data_models import StubEntityORM, UserORM

logger = logging.getLogger(__name__)


class Repository:
    """Single repository for all data access operations.

    Organized using nested classes for clarity:
    - repo.users - user operations
    - repo.stub_entities - scaffolding/example operations

    Future: repo.organizations, repo.projects, repo.tickets, etc.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
        self.users = self.Users(session)
        self.stub_entities = self.StubEntities(session)

    class Users:
        """User-related data access operations."""

        def __init__(self, session: Session) -> None:
            self.session = session

        def create(self, user_create_command: UserCreateCommand) -> User:
            """Create a new user with a generated password.

            Returns the created User domain model (without password_hash).
            The generated password is not returned - it should be captured by the caller
            if needed for display to the user.
            """
            user_data = user_create_command.user_data
            logger.debug(f"Creating new user: {user_data.username}")

            # Generate and hash password
            password_hash = hash_password(generate_password())

            orm_user = UserORM(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                password_hash=password_hash,
                organization_id=user_create_command.organization_id,
                role=user_create_command.role.value,
            )
            self.session.add(orm_user)
            self.session.commit()
            self.session.refresh(orm_user)
            logger.debug(f"User created with ID: {orm_user.id}")
            return orm_user_to_domain_user(orm_user)

        def get_by_id(self, user_id: str) -> Optional[User]:
            """Get a specific user by ID."""
            logger.debug(f"Retrieving user by ID: {user_id}")
            orm_user = self.session.query(UserORM).filter(UserORM.id == user_id).first()  # type: ignore[operator]
            if orm_user is None:
                logger.debug(f"User not found: {user_id}")
                return None
            logger.debug(f"User found: {user_id}")
            return orm_user_to_domain_user(orm_user)

        def get_by_username(self, username: str) -> Optional[User]:
            """Get a specific user by username (case-insensitive).

            Args:
                username: Username to search for (case-insensitive)

            Returns:
                User if found, None otherwise

            Note: Username lookup is case-insensitive to support login requirements.
            """
            logger.debug(f"Retrieving user by username: {username}")
            orm_user = (
                self.session.query(UserORM)
                .filter(func.lower(UserORM.username) == username.lower())  # type: ignore[operator]
                .first()
            )
            if orm_user is None:
                logger.debug(f"User not found: {username}")
                return None
            logger.debug(f"User found: {username}")
            return orm_user_to_domain_user(orm_user)

        def get_by_username_with_password(self, username: str) -> Optional[UserAuthData]:
            """Get user authentication data by username (case-insensitive).

            This method is for authentication purposes only. It returns a domain model
            which includes password_hash for verification.

            Args:
                username: Username to search for (case-insensitive)

            Returns:
                UserAuthData if found (includes password_hash), None otherwise

            Note: Returns a domain model (UserAuthData), never an ORM object.
            This maintains proper layering and prevents ORM leakage.
            """
            logger.debug(f"Retrieving user with password for authentication: {username}")
            orm_user = (
                self.session.query(UserORM)
                .filter(func.lower(UserORM.username) == username.lower())  # type: ignore[operator]
                .first()
            )
            if orm_user is None:
                return None

            return orm_user_to_user_auth_data(orm_user)

        def get_all(self) -> List[User]:
            """Get all users from the database, ordered by creation date."""
            orm_users = self.session.query(UserORM).order_by(UserORM.created_at).all()  # type: ignore[union-attr]
            return [orm_user_to_domain_user(orm_user) for orm_user in orm_users]

        def delete(self, user_id: str) -> bool:
            """Delete a user by ID."""
            logger.debug(f"Deleting user: {user_id}")
            orm_user = self.session.query(UserORM).filter(UserORM.id == user_id).first()  # type: ignore[operator]
            if not orm_user:
                logger.debug(f"User not found for deletion: {user_id}")
                return False

            self.session.delete(orm_user)
            self.session.commit()
            logger.debug(f"User deleted: {user_id}")
            return True

    class StubEntities:
        """Stub entity operations - template/scaffolding for reference."""

        def __init__(self, session: Session) -> None:
            self.session = session

        def get_all(self) -> List[StubEntity]:
            """Get all stub entities from the database, ordered by creation date."""
            orm_stub_entities = self.session.query(StubEntityORM).order_by(StubEntityORM.created_at).all()  # type: ignore[union-attr]
            return orm_stub_entities_to_business_stub_entities(orm_stub_entities)

        def get_by_id(self, stub_entity_id: str) -> Optional[StubEntity]:
            """Get a specific stub entity by ID."""
            logger.debug(f"Retrieving stub entity by ID: {stub_entity_id}")
            orm_stub_entity = self.session.query(StubEntityORM).filter(StubEntityORM.id == stub_entity_id).first()  # type: ignore[operator]
            if orm_stub_entity is None:
                logger.debug(f"Stub entity not found: {stub_entity_id}")
                return None
            logger.debug(f"Stub entity found: {stub_entity_id}")
            return orm_stub_entity_to_business_stub_entity(orm_stub_entity)

        def _get_orm_by_id(self, stub_entity_id: str) -> Optional[StubEntityORM]:
            """Get a specific stub entity by ID as ORM object (for internal use)."""
            logger.debug(f"Retrieving ORM stub entity by ID: {stub_entity_id}")
            return self.session.query(StubEntityORM).filter(StubEntityORM.id == stub_entity_id).first()  # type: ignore[operator]

        def create(self, stub_entity_create_command: StubEntityCreateCommand) -> StubEntity:
            """Create a new stub entity."""
            stub_entity_data = stub_entity_create_command.stub_entity_data
            logger.debug(f"Creating new stub entity: {stub_entity_data.name}")

            orm_stub_entity = StubEntityORM(
                name=stub_entity_data.name,
                description=stub_entity_data.description,
            )
            self.session.add(orm_stub_entity)
            self.session.commit()
            self.session.refresh(orm_stub_entity)
            logger.debug(f"Stub entity created with ID: {orm_stub_entity.id}")
            return orm_stub_entity_to_business_stub_entity(orm_stub_entity)

        def update(self, stub_entity_id: str, stub_entity_data: StubEntityUpdateCommand) -> Optional[StubEntity]:
            """Update an existing stub entity."""
            logger.debug(f"Updating stub entity: {stub_entity_id}")
            stub_entity = self._get_orm_by_id(stub_entity_id)
            if not stub_entity:
                logger.debug(f"Stub entity not found for update: {stub_entity_id}")
                return None

            # Update only the fields that are provided and not None
            update_data = stub_entity_data.model_dump(exclude_unset=True, exclude_none=True)
            if update_data:  # Only proceed if there are fields to update
                for field, value in update_data.items():
                    self.session.query(StubEntityORM).filter(StubEntityORM.id == stub_entity_id).update({field: value})  # type: ignore[operator]

            self.session.commit()
            self.session.refresh(stub_entity)
            logger.debug(f"Stub entity updated: {stub_entity_id}")
            return orm_stub_entity_to_business_stub_entity(stub_entity)

        def delete(self, stub_entity_id: str) -> bool:
            """Delete a stub entity by ID."""
            logger.debug(f"Deleting stub entity: {stub_entity_id}")
            stub_entity = self._get_orm_by_id(stub_entity_id)
            if not stub_entity:
                logger.debug(f"Stub entity not found for deletion: {stub_entity_id}")
                return False

            self.session.delete(stub_entity)
            self.session.commit()
            logger.debug(f"Stub entity deleted: {stub_entity_id}")
            return True


# Legacy classes kept for backward compatibility with existing tests
# TODO: Remove once all tests are migrated to use Repository class


class StubEntityRepository:
    """Legacy wrapper for backward compatibility with existing tests."""

    def __init__(self, session: Session) -> None:
        self._repo = Repository(session).stub_entities

    def get_all_stub_entities(self) -> List[StubEntity]:
        return self._repo.get_all()

    def get_stub_entity_by_id(self, stub_entity_id: str) -> Optional[StubEntity]:
        return self._repo.get_by_id(stub_entity_id)

    def create_stub_entity(self, command: StubEntityCreateCommand) -> StubEntity:
        return self._repo.create(command)

    def update_stub_entity(self, stub_entity_id: str, update_data: StubEntityUpdateCommand) -> Optional[StubEntity]:
        return self._repo.update(stub_entity_id, update_data)

    def delete_stub_entity(self, stub_entity_id: str) -> bool:
        return self._repo.delete(stub_entity_id)


class UserRepository:
    """Legacy wrapper for backward compatibility with existing tests."""

    def __init__(self, session: Session) -> None:
        self._repo = Repository(session).users

    def create_user(self, command: UserCreateCommand) -> User:
        return self._repo.create(command)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self._repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self._repo.get_by_username(username)

    def get_all_users(self) -> List[User]:
        return self._repo.get_all()

    def delete_user(self, user_id: str) -> bool:
        return self._repo.delete(user_id)
