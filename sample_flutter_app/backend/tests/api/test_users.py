"""Atomic HTTP API integration tests for User CRUD Endpoints (SMP-EP1-TK03).

WHY THIS FILE EXISTS:
    Validates the HTTP transport layer for the full User CRUD lifecycle:
    - Create: POST /api/v1/users (201, 400 duplicate email, 422 validation error)
    - Read All: GET /api/v1/users (200 empty list, 200 populated list)
    - Read One: GET /api/v1/users/{user_id} (200, 404 non-existent, 404 malformed ID)
    - Update: PATCH /api/v1/users/{user_id} (200 name/email/password, 400 email conflict, 404)
    - Delete: DELETE /api/v1/users/{user_id} (204, 404 non-existent)
"""

from httpx import AsyncClient

from src.core.security import verify_password
from src.models.user import User


# =============================================================================
# 1. CREATE ENDPOINT TESTS: POST /api/v1/users
# =============================================================================

async def test_create_user_success_returns_201_with_user_out(client: AsyncClient) -> None:
    """POST /api/v1/users creates user and returns 201 Created with UserOut JSON."""
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "SuperSecretPassword123",
    }

    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"


async def test_create_user_shields_password_hash(client: AsyncClient) -> None:
    """POST /api/v1/users response strictly omits password and hashed_password."""
    payload = {
        "name": "Alice Smith",
        "email": "alice_shield@example.com",
        "password": "SuperSecretPassword123",
    }

    response = await client.post("/api/v1/users", json=payload)
    data = response.json()

    assert "password" not in data
    assert "hashed_password" not in data


async def test_create_user_persists_bcrypt_hash_in_database(client: AsyncClient) -> None:
    """POST /api/v1/users hashes the plaintext password before writing to the database."""
    payload = {
        "name": "Alice Smith",
        "email": "alice_hash@example.com",
        "password": "SuperSecretPassword123",
    }

    await client.post("/api/v1/users", json=payload)

    db_user = await User.find_one(User.email == "alice_hash@example.com")
    assert db_user is not None
    assert db_user.password != payload["password"]
    assert verify_password(payload["password"], db_user.password) is True


async def test_create_user_duplicate_email_returns_400(client: AsyncClient) -> None:
    """POST /api/v1/users catches duplicate email registrations and returns HTTP 400."""
    payload = {
        "name": "Bob Jones",
        "email": "bob@example.com",
        "password": "Password456!",
    }

    resp1 = await client.post("/api/v1/users", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/users", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"


async def test_create_user_malformed_email_returns_422(client: AsyncClient) -> None:
    """POST /api/v1/users returns HTTP 422 when email syntax is invalid."""
    payload = {
        "name": "Invalid Email User",
        "email": "not-a-valid-email",
        "password": "Password456!",
    }

    response = await client.post("/api/v1/users", json=payload)
    assert response.status_code == 422


async def test_create_user_missing_required_fields_returns_422(client: AsyncClient) -> None:
    """POST /api/v1/users returns HTTP 422 when required fields are missing."""
    # Missing email
    response = await client.post("/api/v1/users", json={"name": "No Email", "password": "pass"})
    assert response.status_code == 422


# =============================================================================
# 2. READ ALL ENDPOINT TESTS: GET /api/v1/users
# =============================================================================

async def test_list_users_returns_empty_list_when_no_users_exist(client: AsyncClient) -> None:
    """GET /api/v1/users returns an empty list [] on an empty database."""
    response = await client.get("/api/v1/users")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_users_returns_all_persisted_users(client: AsyncClient) -> None:
    """GET /api/v1/users lists all created users."""
    await client.post("/api/v1/users", json={"name": "User 1", "email": "u1@example.com", "password": "password123"})
    await client.post("/api/v1/users", json={"name": "User 2", "email": "u2@example.com", "password": "password123"})

    response = await client.get("/api/v1/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    emails = [u["email"] for u in data]
    assert "u1@example.com" in emails
    assert "u2@example.com" in emails


# =============================================================================
# 3. READ ONE ENDPOINT TESTS: GET /api/v1/users/{user_id}
# =============================================================================

async def test_get_user_by_id_returns_200_and_user_out(client: AsyncClient) -> None:
    """GET /api/v1/users/{id} retrieves matching user profile by ID."""
    create_resp = await client.post(
        "/api/v1/users",
        json={"name": "Charlie", "email": "charlie@example.com", "password": "pass"},
    )
    user_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Charlie"
    assert data["email"] == "charlie@example.com"


async def test_get_user_by_id_nonexistent_returns_404(client: AsyncClient) -> None:
    """GET /api/v1/users/{id} returns 404 when ID does not exist."""
    response = await client.get("/api/v1/users/654321654321654321654321")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


async def test_get_user_by_invalid_id_format_returns_404(client: AsyncClient) -> None:
    """GET /api/v1/users/{id} returns 404 cleanly when ID format is not an ObjectId."""
    response = await client.get("/api/v1/users/invalid-non-hex-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# =============================================================================
# 4. UPDATE ENDPOINT TESTS: PATCH /api/v1/users/{user_id}
# =============================================================================

async def test_update_user_name_returns_200_and_modifies_name(client: AsyncClient) -> None:
    """PATCH /api/v1/users/{id} updates the display name."""
    create_resp = await client.post(
        "/api/v1/users",
        json={"name": "Old Name", "email": "rename@example.com", "password": "pass"},
    )
    user_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/api/v1/users/{user_id}", json={"name": "New Name"})

    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "New Name"

    # Verify DB state
    db_user = await User.get(user_id)
    assert db_user is not None
    assert db_user.name == "New Name"


async def test_update_user_email_returns_200_and_modifies_email(client: AsyncClient) -> None:
    """PATCH /api/v1/users/{id} updates the email address."""
    create_resp = await client.post(
        "/api/v1/users",
        json={"name": "Dave", "email": "dave_old@example.com", "password": "pass"},
    )
    user_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/api/v1/users/{user_id}", json={"email": "dave_new@example.com"})

    assert patch_resp.status_code == 200
    assert patch_resp.json()["email"] == "dave_new@example.com"


async def test_update_user_duplicate_email_returns_400(client: AsyncClient) -> None:
    """PATCH /api/v1/users/{id} returns 400 when attempting to claim another user's email."""
    resp1 = await client.post("/api/v1/users", json={"name": "User A", "email": "userA@example.com", "password": "password123"})
    resp2 = await client.post("/api/v1/users", json={"name": "User B", "email": "userB@example.com", "password": "password123"})
    user2_id = resp2.json()["id"]

    # User B tries to change email to User A's email
    patch_resp = await client.patch(f"/api/v1/users/{user2_id}", json={"email": "userA@example.com"})

    assert patch_resp.status_code == 400
    assert patch_resp.json()["detail"] == "Email already registered"


async def test_update_user_password_hashes_new_password(client: AsyncClient) -> None:
    """PATCH /api/v1/users/{id} hashes updated password and replaces old hash."""
    create_resp = await client.post(
        "/api/v1/users",
        json={"name": "Eve", "email": "eve@example.com", "password": "OldPassword123"},
    )
    user_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/api/v1/users/{user_id}", json={"password": "NewPassword456!"})
    assert patch_resp.status_code == 200

    db_user = await User.get(user_id)
    assert db_user is not None
    assert verify_password("NewPassword456!", db_user.password) is True
    assert verify_password("OldPassword123", db_user.password) is False


async def test_update_user_nonexistent_returns_404(client: AsyncClient) -> None:
    """PATCH /api/v1/users/{id} returns 404 for unknown user ID."""
    response = await client.patch("/api/v1/users/654321654321654321654321", json={"name": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# =============================================================================
# 5. DELETE ENDPOINT TESTS: DELETE /api/v1/users/{user_id}
# =============================================================================

async def test_delete_user_returns_204_and_removes_from_database(client: AsyncClient) -> None:
    """DELETE /api/v1/users/{id} removes user and returns HTTP 204 No Content."""
    create_resp = await client.post(
        "/api/v1/users",
        json={"name": "Delete Me", "email": "deleteme@example.com", "password": "pass"},
    )
    user_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_resp.status_code == 204

    # Verify user is gone
    get_resp = await client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 404


async def test_delete_user_nonexistent_returns_404(client: AsyncClient) -> None:
    """DELETE /api/v1/users/{id} returns 404 when ID does not exist."""
    delete_resp = await client.delete("/api/v1/users/654321654321654321654321")

    assert delete_resp.status_code == 404
    assert delete_resp.json()["detail"] == "User not found"
