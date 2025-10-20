"""Tests for Item API endpoints."""

from fastapi.testclient import TestClient

# Explicitly import pytest fixtures as per project rules
from tests.conftest import client  # noqa: F401


class TestItemAPIEndpoints:
    """Test all item API endpoints for CRUD operations."""

    def test_create_item(self, client: TestClient) -> None:
        """Test creating an item via API."""
        item_data = {"name": "Test Item", "description": "A test item"}
        response = client.post("/items", json=item_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["description"] == "A test item"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_item_without_description(self, client: TestClient) -> None:
        """Test creating an item without description."""
        item_data = {"name": "Item No Description"}
        response = client.post("/items", json=item_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Item No Description"
        assert data["description"] is None

    def test_get_item_by_id(self, client: TestClient) -> None:
        """Test retrieving an item by ID via API."""
        # Create an item first
        item_data = {"name": "Retrievable Item", "description": "Can be retrieved"}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Get the item
        response = client.get(f"/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Retrievable Item"
        assert data["description"] == "Can be retrieved"

    def test_get_item_by_id_not_found(self, client: TestClient) -> None:
        """Test getting a non-existent item returns 404."""
        response = client.get("/items/non-existent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Item not found"

    def test_get_all_items_empty(self, client: TestClient) -> None:
        """Test getting all items when database is empty."""
        response = client.get("/items")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_all_items_with_data(self, client: TestClient) -> None:
        """Test getting all items when database has data."""
        # Create multiple items
        item1_data = {"name": "Item 1", "description": "First item"}
        item2_data = {"name": "Item 2", "description": "Second item"}
        client.post("/items", json=item1_data)
        client.post("/items", json=item2_data)

        # Get all items
        response = client.get("/items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        item_names = {item["name"] for item in data}
        assert item_names == {"Item 1", "Item 2"}

    def test_delete_item(self, client: TestClient) -> None:
        """Test deleting an item via API."""
        # Create an item first
        item_data = {"name": "Delete Me", "description": "Will be deleted"}
        create_response = client.post("/items", json=item_data)
        created_item = create_response.json()
        item_id = created_item["id"]

        # Delete the item
        response = client.delete(f"/items/{item_id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify it's gone
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client: TestClient) -> None:
        """Test deleting a non-existent item returns 404."""
        response = client.delete("/items/non-existent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Item not found"


class TestItemAPICRUDWorkflow:
    """Test complete CRUD workflow for items."""

    def test_complete_crud_workflow(self, client: TestClient) -> None:
        """Test a complete CRUD workflow for an item."""
        # 1. Create an item
        item_data = {"name": "Workflow Item", "description": "Full CRUD test"}
        create_response = client.post("/items", json=item_data)
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item["id"]

        # 2. Read the item
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 200
        item = get_response.json()
        assert item["name"] == "Workflow Item"
        assert item["description"] == "Full CRUD test"

        # 3. Verify it appears in list
        list_response = client.get("/items")
        assert list_response.status_code == 200
        items = list_response.json()
        assert len(items) == 1
        assert items[0]["id"] == item_id

        # 4. Delete the item
        delete_response = client.delete(f"/items/{item_id}")
        assert delete_response.status_code == 204

        # 5. Verify deletion
        final_get_response = client.get(f"/items/{item_id}")
        assert final_get_response.status_code == 404

        # 6. Verify list is empty
        final_list_response = client.get("/items")
        assert final_list_response.status_code == 200
        final_items = final_list_response.json()
        assert len(final_items) == 0
