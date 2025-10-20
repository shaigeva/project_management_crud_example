"""Repository classes for data access operations.

This module provides repository classes that handle all database operations
for the project management application, following the Repository pattern to
separate business logic from data access logic.

The StubEntityRepository serves as a template/scaffolding for creating real repositories.
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from project_management_crud_example.domain_models import (
    StubEntity,
    StubEntityCreateCommand,
    StubEntityUpdateCommand,
)

from .converters import (
    orm_stub_entities_to_business_stub_entities,
    orm_stub_entity_to_business_stub_entity,
)
from .orm_data_models import StubEntityORM

logger = logging.getLogger(__name__)


class StubEntityRepository:
    """Repository class for stub entity CRUD operations - template for creating real repositories."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    def get_all_stub_entities(self) -> List[StubEntity]:
        """Get all stub entities from the database, ordered by creation date."""
        orm_stub_entities = self.session.query(StubEntityORM).order_by(StubEntityORM.created_at).all()  # type: ignore[union-attr]
        return orm_stub_entities_to_business_stub_entities(orm_stub_entities)

    def get_stub_entity_by_id(self, stub_entity_id: str) -> Optional[StubEntity]:
        """Get a specific stub entity by ID."""
        logger.debug(f"Retrieving stub entity by ID: {stub_entity_id}")
        orm_stub_entity = self.session.query(StubEntityORM).filter(StubEntityORM.id == stub_entity_id).first()  # type: ignore[operator]
        if orm_stub_entity is None:
            logger.debug(f"Stub entity not found: {stub_entity_id}")
            return None
        logger.debug(f"Stub entity found: {stub_entity_id}")
        return orm_stub_entity_to_business_stub_entity(orm_stub_entity)

    def _get_orm_stub_entity_by_id(self, stub_entity_id: str) -> Optional[StubEntityORM]:
        """Get a specific stub entity by ID as ORM object (for internal use)."""
        logger.debug(f"Retrieving ORM stub entity by ID: {stub_entity_id}")
        return self.session.query(StubEntityORM).filter(StubEntityORM.id == stub_entity_id).first()  # type: ignore[operator]

    def create_stub_entity(self, stub_entity_create_command: StubEntityCreateCommand) -> StubEntity:
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

    def update_stub_entity(
        self, stub_entity_id: str, stub_entity_data: StubEntityUpdateCommand
    ) -> Optional[StubEntity]:
        """Update an existing stub entity."""
        logger.debug(f"Updating stub entity: {stub_entity_id}")
        stub_entity = self._get_orm_stub_entity_by_id(stub_entity_id)
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

    def delete_stub_entity(self, stub_entity_id: str) -> bool:
        """Delete a stub entity by ID."""
        logger.debug(f"Deleting stub entity: {stub_entity_id}")
        stub_entity = self._get_orm_stub_entity_by_id(stub_entity_id)
        if not stub_entity:
            logger.debug(f"Stub entity not found for deletion: {stub_entity_id}")
            return False

        self.session.delete(stub_entity)
        self.session.commit()
        logger.debug(f"Stub entity deleted: {stub_entity_id}")
        return True
