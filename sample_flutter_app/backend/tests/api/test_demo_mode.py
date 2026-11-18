"""Integration tests for In-Memory Demo Mode and Startup Seeding (SMP-EP1-TK05).

WHY THIS FILE EXISTS:
    Validates that when the application runs in demo mode (the default for local
    probing with Postman, curl, or Swagger UI):
    1. The in-memory database initializes automatically via lifespan.
    2. Initial demo accounts (Alice and Bob) are pre-seeded.
    3. Initial demo tasks are pre-seeded and properly user-scoped.
"""

from collections.abc import AsyncGenerator
from httpx import ASGITransport, AsyncClient
import pytest_asyncio

from src.core.config import settings
from src.core.database import init_db
from src.main import create_app
from src.models.task import Task
from src.models.user import User


@pytest_asyncio.fixture
async def demo_client() -> AsyncGenerator[AsyncClient, None]:
    """Client fixture that forces demo mode to verify startup seeding."""
    # Temporarily set app_env to demo
    original_env = settings.app_env
    settings.app_env = "demo"

    # Purge any existing state and re-initialize in demo mode
    await User.delete_all()
    await Task.delete_all()
    await init_db()

    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    # Restore environment and clean up
    settings.app_env = original_env
    await User.delete_all()
    await Task.delete_all()


async def test_demo_mode_seeds_initial_users(demo_client: AsyncClient) -> None:
    """Verifies that launching in demo mode seeds Alice Smith and Bob Jones."""
    response = await demo_client.get("/api/v1/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    emails = [u["email"] for u in data]
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails


async def test_demo_mode_seeds_user_scoped_tasks(demo_client: AsyncClient) -> None:
    """Verifies that demo mode seeds initial tasks correctly linked to Alice and Bob."""
    users_resp = await demo_client.get("/api/v1/users")
    users = users_resp.json()

    alice = next(u for u in users if u["email"] == "alice@example.com")
    bob = next(u for u in users if u["email"] == "bob@example.com")

    # 1. Verify Alice's pre-seeded tasks
    alice_tasks_resp = await demo_client.get(f"/api/v1/tasks?user_id={alice['id']}")
    assert alice_tasks_resp.status_code == 200
    alice_tasks = alice_tasks_resp.json()
    assert len(alice_tasks) == 3
    alice_titles = [t["name"] for t in alice_tasks]
    assert "Explore FastAPI Swagger documentation at /docs" in alice_titles

    # 2. Verify Bob's pre-seeded task
    bob_tasks_resp = await demo_client.get(f"/api/v1/tasks?user_id={bob['id']}")
    assert bob_tasks_resp.status_code == 200
    bob_tasks = bob_tasks_resp.json()
    assert len(bob_tasks) == 1
    assert bob_tasks[0]["name"] == "Review FHIR task alignment and roadmap"
