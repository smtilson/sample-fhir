"""Atomic HTTP API integration tests for Task CRUD Endpoints (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Validates the HTTP transport layer for the complete user-scoped Task lifecycle:
    - Create: POST /api/v1/tasks (201, 400 user does not exist, 422 validation error)
    - Read All: GET /api/v1/tasks (200 empty list, 200 all tasks, 200 filtered by ?user_id=...)
    - Read One: GET /api/v1/tasks/{task_id} (200, 404 non-existent, 404 malformed ID)
    - Update: PATCH /api/v1/tasks/{task_id} (200 name/completion/metadata, 404)
    - Delete: DELETE /api/v1/tasks/{task_id} (204, 404 non-existent)
"""

from httpx import AsyncClient

from src.models.user import User


# =============================================================================
# 1. CREATE ENDPOINT TESTS: POST /api/v1/tasks
# =============================================================================

async def test_create_task_success_returns_201_with_task_out(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """POST /api/v1/tasks creates a task scoped to user and returns 201 Created."""
    user_id = str(persisted_user.id)
    payload = {
        "user_id": user_id,
        "name": "Integration Test Task",
        "is_completed": False,
        "metadata": {"priority": "urgent", "tag": "test"},
    }

    response = await client.post("/api/v1/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == user_id
    assert data["name"] == "Integration Test Task"
    assert data["is_completed"] is False
    assert data["metadata"] == {"priority": "urgent", "tag": "test"}


async def test_create_task_with_default_values(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """POST /api/v1/tasks applies default values when optional fields are omitted."""
    user_id = str(persisted_user.id)
    payload = {
        "user_id": user_id,
        "name": "Task with Defaults",
    }

    response = await client.post("/api/v1/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["is_completed"] is False
    assert data["metadata"] == {}


async def test_create_task_with_nonexistent_user_returns_400(
    client: AsyncClient,
) -> None:
    """POST /api/v1/tasks returns 400 Bad Request when user_id does not exist."""
    payload = {
        "user_id": "654321654321654321654321",
        "name": "Orphaned Task",
    }

    response = await client.post("/api/v1/tasks", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User does not exist"


async def test_create_task_with_invalid_user_id_format_returns_400(
    client: AsyncClient,
) -> None:
    """POST /api/v1/tasks returns 400 Bad Request when user_id is not a valid ObjectId string."""
    payload = {
        "user_id": "invalid-non-hex-id",
        "name": "Malformed User ID Task",
    }

    response = await client.post("/api/v1/tasks", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "User does not exist"


async def test_create_task_missing_required_fields_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/tasks returns HTTP 422 when name is missing."""
    response = await client.post("/api/v1/tasks", json={"user_id": "123"})
    assert response.status_code == 422


async def test_create_task_empty_name_returns_422(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """POST /api/v1/tasks returns HTTP 422 when name is empty string."""
    payload = {"user_id": str(persisted_user.id), "name": ""}
    response = await client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422


# =============================================================================
# 2. READ ALL ENDPOINT TESTS: GET /api/v1/tasks
# =============================================================================

async def test_list_tasks_returns_empty_list_when_none_exist(
    client: AsyncClient,
) -> None:
    """GET /api/v1/tasks returns an empty list [] on a clean database."""
    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_tasks_returns_all_tasks(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """GET /api/v1/tasks returns all tasks across users."""
    uid = str(persisted_user.id)
    await client.post("/api/v1/tasks", json={"user_id": uid, "name": "Task 1"})
    await client.post("/api/v1/tasks", json={"user_id": uid, "name": "Task 2"})

    response = await client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_list_tasks_filtered_by_user_id(
    client: AsyncClient,
    persisted_users: list[User],
) -> None:
    """GET /api/v1/tasks?user_id=... returns only tasks for that specific user."""
    user1_id = str(persisted_users[0].id)
    user2_id = str(persisted_users[1].id)

    # Create task for User 1
    await client.post("/api/v1/tasks", json={"user_id": user1_id, "name": "User 1 Task"})
    # Create task for User 2
    await client.post("/api/v1/tasks", json={"user_id": user2_id, "name": "User 2 Task"})

    # Query filtered by user 1
    response = await client.get(f"/api/v1/tasks?user_id={user1_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "User 1 Task"
    assert data[0]["user_id"] == user1_id


# =============================================================================
# 3. READ ONE ENDPOINT TESTS: GET /api/v1/tasks/{task_id}
# =============================================================================

async def test_get_task_by_id_returns_200_and_task_out(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """GET /api/v1/tasks/{id} retrieves matching task by ID."""
    uid = str(persisted_user.id)
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"user_id": uid, "name": "Specific Task", "is_completed": True},
    )
    task_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["name"] == "Specific Task"
    assert data["is_completed"] is True


async def test_get_task_by_id_nonexistent_returns_404(
    client: AsyncClient,
) -> None:
    """GET /api/v1/tasks/{id} returns 404 when task ID does not exist."""
    response = await client.get("/api/v1/tasks/654321654321654321654321")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


async def test_get_task_by_invalid_id_format_returns_404(
    client: AsyncClient,
) -> None:
    """GET /api/v1/tasks/{id} returns 404 cleanly when ID is not an ObjectId."""
    response = await client.get("/api/v1/tasks/invalid-hex-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# =============================================================================
# 4. UPDATE ENDPOINT TESTS: PATCH /api/v1/tasks/{task_id}
# =============================================================================

async def test_update_task_name_returns_200_and_modifies_name(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """PATCH /api/v1/tasks/{id} updates the task name."""
    uid = str(persisted_user.id)
    create_resp = await client.post("/api/v1/tasks", json={"user_id": uid, "name": "Old Name"})
    task_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/api/v1/tasks/{task_id}", json={"name": "New Name"})

    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "New Name"


async def test_update_task_toggle_completion_returns_200(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """PATCH /api/v1/tasks/{id} toggles is_completed status."""
    uid = str(persisted_user.id)
    create_resp = await client.post(
        "/api/v1/tasks",
        json={"user_id": uid, "name": "Toggle Task", "is_completed": False},
    )
    task_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/api/v1/tasks/{task_id}", json={"is_completed": True})

    assert patch_resp.status_code == 200
    assert patch_resp.json()["is_completed"] is True


async def test_update_task_metadata_returns_200(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """PATCH /api/v1/tasks/{id} updates the metadata dictionary."""
    uid = str(persisted_user.id)
    create_resp = await client.post("/api/v1/tasks", json={"user_id": uid, "name": "Meta Task"})
    task_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"metadata": {"priority": "critical"}},
    )

    assert patch_resp.status_code == 200
    assert patch_resp.json()["metadata"] == {"priority": "critical"}


async def test_update_task_nonexistent_returns_404(
    client: AsyncClient,
) -> None:
    """PATCH /api/v1/tasks/{id} returns 404 for unknown task ID."""
    response = await client.patch("/api/v1/tasks/654321654321654321654321", json={"name": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# =============================================================================
# 5. DELETE ENDPOINT TESTS: DELETE /api/v1/tasks/{task_id}
# =============================================================================

async def test_delete_task_returns_204_and_removes_from_database(
    client: AsyncClient,
    persisted_user: User,
) -> None:
    """DELETE /api/v1/tasks/{id} deletes the task and returns HTTP 204 No Content."""
    uid = str(persisted_user.id)
    create_resp = await client.post("/api/v1/tasks", json={"user_id": uid, "name": "Delete Me"})
    task_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_resp.status_code == 204

    # Verify task no longer exists
    get_resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert get_resp.status_code == 404


async def test_delete_task_nonexistent_returns_404(
    client: AsyncClient,
) -> None:
    """DELETE /api/v1/tasks/{id} returns 404 when task ID does not exist."""
    delete_resp = await client.delete("/api/v1/tasks/654321654321654321654321")

    assert delete_resp.status_code == 404
    assert delete_resp.json()["detail"] == "Task not found"
