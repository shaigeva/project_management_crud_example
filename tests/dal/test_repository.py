"""Tests for the ItemRepository class."""

from project_management_crud_example.dal.sqlite.repository import ItemRepository
from project_management_crud_example.domain_models import ItemCreateCommand, ItemData

# Explicitly import pytest fixtures as per project rules
from tests.conftest import test_item_repo  # noqa: F401


class TestItemRepository:
    """Test the ItemRepository CRUD operations."""

    def test_create_item(self, test_item_repo: ItemRepository) -> None:
        """Test creating an item in the database."""
        item_data = ItemData(name="Test Item", description="A test item")
        item_create_command = ItemCreateCommand(item_data=item_data)

        item = test_item_repo.create_item(item_create_command)

        assert item.name == "Test Item"
        assert item.description == "A test item"
        assert item.id is not None
        assert item.created_at is not None
        assert item.updated_at is not None

    def test_get_item_by_id(self, test_item_repo: ItemRepository) -> None:
        """Test retrieving an item by ID."""
        # Create an item
        item_data = ItemData(name="Retrievable Item", description="Can be retrieved")
        item_create_command = ItemCreateCommand(item_data=item_data)
        created_item = test_item_repo.create_item(item_create_command)

        # Retrieve it
        retrieved_item = test_item_repo.get_item_by_id(created_item.id)

        assert retrieved_item is not None
        assert retrieved_item.id == created_item.id
        assert retrieved_item.name == "Retrievable Item"
        assert retrieved_item.description == "Can be retrieved"

    def test_get_item_by_id_not_found(self, test_item_repo: ItemRepository) -> None:
        """Test retrieving a non-existent item returns None."""
        retrieved_item = test_item_repo.get_item_by_id("non-existent-id")

        assert retrieved_item is None

    def test_get_all_items(self, test_item_repo: ItemRepository) -> None:
        """Test retrieving all items."""
        # Create multiple items
        item1_data = ItemData(name="Item 1", description="First item")
        item2_data = ItemData(name="Item 2", description="Second item")

        test_item_repo.create_item(ItemCreateCommand(item_data=item1_data))
        test_item_repo.create_item(ItemCreateCommand(item_data=item2_data))

        # Get all items
        all_items = test_item_repo.get_all_items()

        assert len(all_items) == 2
        item_names = {item.name for item in all_items}
        assert item_names == {"Item 1", "Item 2"}

    def test_get_all_items_empty(self, test_item_repo: ItemRepository) -> None:
        """Test retrieving all items when database is empty."""
        all_items = test_item_repo.get_all_items()

        assert all_items == []

    def test_delete_item(self, test_item_repo: ItemRepository) -> None:
        """Test deleting an item."""
        # Create an item
        item_data = ItemData(name="Delete Me", description="Will be deleted")
        item_create_command = ItemCreateCommand(item_data=item_data)
        created_item = test_item_repo.create_item(item_create_command)

        # Delete it
        success = test_item_repo.delete_item(created_item.id)

        assert success is True

        # Verify it's gone
        retrieved_item = test_item_repo.get_item_by_id(created_item.id)
        assert retrieved_item is None

    def test_delete_item_not_found(self, test_item_repo: ItemRepository) -> None:
        """Test deleting a non-existent item returns False."""
        success = test_item_repo.delete_item("non-existent-id")

        assert success is False
