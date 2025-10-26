"""Tests for epic API endpoints."""

from fastapi.testclient import TestClient

from tests.conftest import client  # noqa: F401
from tests.fixtures.auth_fixtures import (  # noqa: F401
    org_admin_token,
    project_manager_token,
    read_user_token,
    super_admin_token,
    write_user_token,
)
from tests.helpers import auth_headers, create_admin_user, create_project_manager, create_test_epic, create_test_org


class TestCreateEpic:
    """Tests for POST /api/epics endpoint."""

    def test_create_epic_as_admin(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test creating epic as Admin."""
        token, org_id = org_admin_token
        epic_data = {"name": "Launch V1", "description": "MVP launch epic"}

        response = client.post("/api/epics", json=epic_data, headers=auth_headers(token))

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Launch V1"
        assert data["description"] == "MVP launch epic"
        assert data["organization_id"] == org_id
        assert "id" in data

    def test_create_epic_as_project_manager(self, client: TestClient, project_manager_token: tuple[str, str]) -> None:
        """Test creating epic as Project Manager."""
        token, org_id = project_manager_token
        epic_data = {"name": "Q1 Goals"}

        response = client.post("/api/epics", json=epic_data, headers=auth_headers(token))

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Q1 Goals"

    def test_create_epic_as_write_user_fails(self, client: TestClient, write_user_token: tuple[str, str]) -> None:
        """Test that Write user cannot create epics."""
        token, _ = write_user_token
        epic_data = {"name": "Unauthorized Epic"}

        response = client.post("/api/epics", json=epic_data, headers=auth_headers(token))

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_create_epic_without_description(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test creating epic without optional description."""
        token, _ = org_admin_token
        epic_data = {"name": "Name Only Epic"}

        response = client.post("/api/epics", json=epic_data, headers=auth_headers(token))

        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None

    def test_create_epic_validation_empty_name(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test creating epic with empty name fails validation."""
        token, _ = org_admin_token
        epic_data = {"name": ""}

        response = client.post("/api/epics", json=epic_data, headers=auth_headers(token))

        assert response.status_code == 422


class TestGetEpic:
    """Tests for GET /api/epics/{id} endpoint."""

    def test_get_epic_by_id(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test retrieving epic by ID."""
        token, org_id = org_admin_token
        epic_id = create_test_epic(client, token, "Test Epic")

        response = client.get(f"/api/epics/{epic_id}", headers=auth_headers(token))

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == epic_id
        assert data["name"] == "Test Epic"

    def test_get_epic_not_found(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test getting non-existent epic returns 404."""
        token, _ = org_admin_token

        response = client.get("/api/epics/nonexistent-id", headers=auth_headers(token))

        assert response.status_code == 404

    def test_get_epic_from_different_org_fails(
        self, client: TestClient, org_admin_token: tuple[str, str], super_admin_token: str
    ) -> None:
        """Test cannot get epic from different organization."""
        token, _ = org_admin_token

        # Create epic in different org
        other_org_id = create_test_org(client, super_admin_token, "Other Org")
        _, other_admin_password = create_admin_user(client, super_admin_token, other_org_id, username="other_admin")
        login_resp = client.post("/auth/login", json={"username": "other_admin", "password": other_admin_password})
        other_token = login_resp.json()["access_token"]
        epic_id = create_test_epic(client, other_token, "Other Epic")

        # Try to get from first org
        response = client.get(f"/api/epics/{epic_id}", headers=auth_headers(token))

        assert response.status_code == 403
        assert "different organization" in response.json()["detail"]


class TestListEpics:
    """Tests for GET /api/epics endpoint."""

    def test_list_epics_in_organization(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test listing epics returns only organization's epics."""
        token, org_id = org_admin_token

        create_test_epic(client, token, "Epic 1")
        create_test_epic(client, token, "Epic 2")

        response = client.get("/api/epics", headers=auth_headers(token))

        assert response.status_code == 200
        epics = response.json()
        assert len(epics) == 2
        assert all(e["organization_id"] == org_id for e in epics)

    def test_list_epics_empty(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test listing epics when none exist returns empty array."""
        token, _ = org_admin_token

        response = client.get("/api/epics", headers=auth_headers(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_list_epics_super_admin_sees_all(
        self, client: TestClient, super_admin_token: str, org_admin_token: tuple[str, str]
    ) -> None:
        """Test Super Admin sees epics from all organizations."""
        # Create epic in org
        org_token, _ = org_admin_token
        create_test_epic(client, org_token, "Org Epic")

        # Super Admin lists all
        response = client.get("/api/epics", headers=auth_headers(super_admin_token))

        assert response.status_code == 200
        epics = response.json()
        assert len(epics) >= 1  # At least the one we created


class TestUpdateEpic:
    """Tests for PUT /api/epics/{id} endpoint."""

    def test_update_epic_name(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test updating epic name."""
        token, _ = org_admin_token
        epic_id = create_test_epic(client, token, "Old Name")

        response = client.put(f"/api/epics/{epic_id}", json={"name": "New Name"}, headers=auth_headers(token))

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"

    def test_update_epic_description(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test updating epic description."""
        token, _ = org_admin_token
        epic_id = create_test_epic(client, token, "Epic")

        response = client.put(
            f"/api/epics/{epic_id}", json={"description": "New description"}, headers=auth_headers(token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New description"

    def test_update_epic_as_project_manager(self, client: TestClient, project_manager_token: tuple[str, str]) -> None:
        """Test Project Manager can update epic."""
        token, _ = project_manager_token
        epic_id = create_test_epic(client, token, "PM Epic")

        response = client.put(f"/api/epics/{epic_id}", json={"name": "Updated"}, headers=auth_headers(token))

        assert response.status_code == 200

    def test_update_epic_as_write_user_fails(
        self, client: TestClient, write_user_token: tuple[str, str], super_admin_token: str
    ) -> None:
        """Test Write user cannot update epic."""
        write_token, org_id = write_user_token

        # Create PM to create epic
        _, pm_password = create_project_manager(client, super_admin_token, org_id, username="pm_for_update")
        login_resp = client.post("/auth/login", json={"username": "pm_for_update", "password": pm_password})
        pm_token = login_resp.json()["access_token"]
        epic_id = create_test_epic(client, pm_token, "Epic")

        # Try to update as write user
        response = client.put(f"/api/epics/{epic_id}", json={"name": "Hacked"}, headers=auth_headers(write_token))

        assert response.status_code == 403

    def test_update_epic_not_found(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test updating non-existent epic returns 404."""
        token, _ = org_admin_token

        response = client.put("/api/epics/nonexistent", json={"name": "New"}, headers=auth_headers(token))

        assert response.status_code == 404


class TestDeleteEpic:
    """Tests for DELETE /api/epics/{id} endpoint."""

    def test_delete_epic_as_admin(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test deleting epic as Admin."""
        token, _ = org_admin_token
        epic_id = create_test_epic(client, token, "To Delete")

        response = client.delete(f"/api/epics/{epic_id}", headers=auth_headers(token))

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/epics/{epic_id}", headers=auth_headers(token))
        assert get_response.status_code == 404

    def test_delete_epic_as_project_manager_fails(
        self, client: TestClient, project_manager_token: tuple[str, str]
    ) -> None:
        """Test Project Manager cannot delete epic."""
        token, _ = project_manager_token
        epic_id = create_test_epic(client, token, "PM Epic")

        response = client.delete(f"/api/epics/{epic_id}", headers=auth_headers(token))

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_delete_epic_not_found(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test deleting non-existent epic returns 404."""
        token, _ = org_admin_token

        response = client.delete("/api/epics/nonexistent", headers=auth_headers(token))

        assert response.status_code == 404


class TestEpicWorkflows:
    """Test complete epic workflows."""

    def test_complete_epic_crud_workflow(self, client: TestClient, org_admin_token: tuple[str, str]) -> None:
        """Test complete CRUD workflow for an epic."""
        token, org_id = org_admin_token

        # 1. Create epic
        create_response = client.post(
            "/api/epics", json={"name": "Workflow Epic", "description": "Test"}, headers=auth_headers(token)
        )
        assert create_response.status_code == 201
        epic_id = create_response.json()["id"]

        # 2. Get epic
        get_response = client.get(f"/api/epics/{epic_id}", headers=auth_headers(token))
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Workflow Epic"

        # 3. List epics
        list_response = client.get("/api/epics", headers=auth_headers(token))
        assert any(e["id"] == epic_id for e in list_response.json())

        # 4. Update epic
        update_response = client.put(
            f"/api/epics/{epic_id}", json={"name": "Updated Epic"}, headers=auth_headers(token)
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Epic"

        # 5. Delete epic
        delete_response = client.delete(f"/api/epics/{epic_id}", headers=auth_headers(token))
        assert delete_response.status_code == 204

        # 6. Verify deletion
        final_get = client.get(f"/api/epics/{epic_id}", headers=auth_headers(token))
        assert final_get.status_code == 404
