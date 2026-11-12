"""HTTP API integration tests for User Endpoints (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Validates the HTTP transport contract for user management endpoints:
    1. POST /api/v1/users: validates payload, creates user, returns 201 Created.
    2. Response shielding: UserOut schema prevents leaking password hashes over HTTP.
    3. Error mapping: verifies the endpoint catches duplicate email attempts and
       maps them to a clean HTTP 400 Bad Request with a clear error detail message.
    4. GET /api/v1/users: lists existing users for the Flutter active-user switcher.
    5. GET /api/v1/users/{id}: retrieves user profile by ID or returns 404 Not Found.
"""

from httpx import AsyncClient

from src.core.security import verify_password
from src.models.user import User


async def test_create_user_returns_201_and_hides_password(client: AsyncClient) -> None:
    """POST /api/v1/users creates user, returns 201, and shields sensitive credentials."""
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "SuperSecretPassword123",
    }

    response = await client.post("/api/v1/users", json=payload)

    # 1. HTTP 201 Created
    assert response.status_code == 201

    data = response.json()
    # 2. Public response contains id, name, email
    assert "id" in data
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"

    # 3. CRITICAL: Public response must NEVER return password or password hash
    assert "password" not in data
    assert "hashed_password" not in data

    # 4. Verify in-memory DB persistence: password is saved as bcrypt hash
    db_user = await User.find_one(User.email == "alice@example.com")
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

    # First registration succeeds
    resp1 = await client.post("/api/v1/users", json=payload)
    assert resp1.status_code == 201

    # Second registration with same email must be caught and mapped to HTTP 400
    resp2 = await client.post("/api/v1/users", json=payload)
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"


async def test_list_users_returns_registered_users(client: AsyncClient) -> None:
    """GET /api/v1/users lists all created users for the Flutter user switcher."""
    # Register two users
    await client.post("/api/v1/users", json={
        "name": "User One", "email": "user1@example.com", "password": "pass1234"
    })
    await client.post("/api/v1/users", json={
        "name": "User Two", "email": "user2@example.com", "password": "pass1234"
    })

    response = await client.get("/api/v1/users")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    emails = [u["email"] for u in data]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails


async def test_get_user_by_id_returns_user_and_404_for_unknown(client: AsyncClient) -> None:
    """GET /api/v1/users/{id} retrieves user by ID or returns 404 if not found."""
    # Create a user
    resp = await client.post("/api/v1/users", json={
        "name": "Charlie Brown", "email": "charlie@example.com", "password": "pass1234"
    })
    user_id = resp.json()["id"]

    # 1. Fetch valid ID
    get_resp = await client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Charlie Brown"

    # 2. Fetch non-existent ID
    not_found_resp = await client.get("/api/v1/users/654321654321654321654321")
    assert not_found_resp.status_code == 404
    assert not_found_resp.json()["detail"] == "User not found"
