"""Repository classes for data access operations.

This module provides repository classes that handle all database operations
for the project management application, following the Repository pattern to
separate business logic from data access logic.
"""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from project_management_crud_example.domain_models import (
    Item,
    ItemCreateCommand,
    ItemUpdateCommand,
)

from .converters import (
    orm_item_to_business_item,
    orm_items_to_business_items,
)
from .orm_data_models import ItemORM

logger = logging.getLogger(__name__)


class ItemRepository:
    """Repository class for item CRUD operations."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    def get_all_items(self) -> List[Item]:
        """Get all items from the database, ordered by creation date."""
        orm_items = self.session.query(ItemORM).order_by(ItemORM.created_at).all()  # type: ignore[union-attr]
        return orm_items_to_business_items(orm_items)

    def get_item_by_id(self, item_id: str) -> Optional[Item]:
        """Get a specific item by ID."""
        logger.debug(f"Retrieving item by ID: {item_id}")
        orm_item = self.session.query(ItemORM).filter(ItemORM.id == item_id).first()  # type: ignore[operator]
        if orm_item is None:
            logger.debug(f"Item not found: {item_id}")
            return None
        logger.debug(f"Item found: {item_id}")
        return orm_item_to_business_item(orm_item)

    def _get_orm_item_by_id(self, item_id: str) -> Optional[ItemORM]:
        """Get a specific item by ID as ORM object (for internal use)."""
        logger.debug(f"Retrieving ORM item by ID: {item_id}")
        return self.session.query(ItemORM).filter(ItemORM.id == item_id).first()  # type: ignore[operator]

    def create_item(self, item_create_command: ItemCreateCommand) -> Item:
        """Create a new item."""
        item_data = item_create_command.item_data
        logger.debug(f"Creating new item: {item_data.name}")

        orm_item = ItemORM(
            name=item_data.name,
            description=item_data.description,
        )
        self.session.add(orm_item)
        self.session.commit()
        self.session.refresh(orm_item)
        logger.debug(f"Item created with ID: {orm_item.id}")
        return orm_item_to_business_item(orm_item)

    def update_item(self, item_id: str, item_data: ItemUpdateCommand) -> Optional[Item]:
        """Update an existing item."""
        logger.debug(f"Updating item: {item_id}")
        item = self._get_orm_item_by_id(item_id)
        if not item:
            logger.debug(f"Item not found for update: {item_id}")
            return None

        # Update only the fields that are provided and not None
        update_data = item_data.model_dump(exclude_unset=True, exclude_none=True)
        if update_data:  # Only proceed if there are fields to update
            for field, value in update_data.items():
                self.session.query(ItemORM).filter(ItemORM.id == item_id).update({field: value})  # type: ignore[operator]

        self.session.commit()
        self.session.refresh(item)
        logger.debug(f"Item updated: {item_id}")
        return orm_item_to_business_item(item)

    def delete_item(self, item_id: str) -> bool:
        """Delete an item by ID."""
        logger.debug(f"Deleting item: {item_id}")
        item = self._get_orm_item_by_id(item_id)
        if not item:
            logger.debug(f"Item not found for deletion: {item_id}")
            return False

        self.session.delete(item)
        self.session.commit()
        logger.debug(f"Item deleted: {item_id}")
        return True
