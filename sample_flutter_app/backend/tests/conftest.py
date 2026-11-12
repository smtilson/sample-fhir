"""Shared pytest fixtures (SMP-EP0-TK01 & SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    `conftest.py` provides shared fixtures for unit and API tests:
    1. `client`: Async HTTP test client bound in-process to `create_app()`.
    2. `init_test_db`: Autouse async fixture initializing Beanie ODM with an
       in-memory `mongomock-motor` database for fast, isolated tests.
    3. `sample_users_raw_data`: Fixture providing raw dictionary data for creating users.
    4. `persisted_users`: Fixture taking raw data and inserting User documents into the DB.
    5. `persisted_user`: Convenience fixture providing a single persisted User document.
"""

from collections.abc import AsyncGenerator
from typing import Any

import mongomock.database
import mongomock_motor
import pytest
import pytest_asyncio
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient

from src.main import create_app
from src.models.user import User

# -----------------------------------------------------------------------------
# Upstream Compatibility Shim (ISSUE-DEP-03):
# Beanie 1.25+ passes `authorizedCollections=True` and `nameOnly=True` to
# `list_collection_names()`. mongomock has not updated its signature to accept
# these server-hint kwargs, causing a TypeError during `init_beanie()`.
# We shim mongomock's Database.list_collection_names to strip them safely.
# -----------------------------------------------------------------------------
_orig_list_collection_names = mongomock.database.Database.list_collection_names


def _patched_list_collection_names(self: Any, *args: Any, **kwargs: Any) -> list[str]:
    kwargs.pop("authorizedCollections", None)
    kwargs.pop("nameOnly", None)
    return _orig_list_collection_names(self, *args, **kwargs)


mongomock.database.Database.list_collection_names = _patched_list_collection_names


@pytest_asyncio.fixture(autouse=True)
async def init_test_db() -> AsyncGenerator[None, None]:
    """Initialize an in-memory MongoDB mock database with Beanie document models.

    Runs automatically before every test to guarantee test isolation. Clears
    collections upon teardown so tests cannot leak state into each other.
    """
    mock_client = mongomock_motor.AsyncMongoMockClient()
    test_db = mock_client["test_todo_db"]

    await init_beanie(
        database=test_db,
        document_models=[User],
    )

    yield

    # Teardown: ensure all documents are purged between test runs
    await User.delete_all()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an async HTTP client bound to a freshly built app instance.

    Function scope (the default) is intentional: every test gets a clean app.
    `base_url` is a placeholder — ASGITransport never hits the network, but
    httpx requires an absolute URL to build requests.
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.fixture
def sample_users_raw_data() -> list[dict[str, Any]]:
    """Provide a list of dictionaries containing raw user data for model instantiation."""
    return [
        {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "password": "$2b$12$e80yq9Y1pGv8qL8Z8hP9uODhM.K5XG1V1jZqF8bA1mK8Y0a1b2c3d",
        },
        {
            "name": "Bob Jones",
            "email": "bob@example.com",
            "password": "$2b$12$k91zr0Z2qHw9rM9a9iQ0vPEiN.L6YH2W2kArG9cB2nL9Z1b2c3d4e",
        },
        {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "password": "$2b$12$m02as1A3rIx0sN0b0jR1wQFjO.M7ZI3X3lBsH0dC3oM0a2c3d4e5f",
        },
    ]


@pytest_asyncio.fixture
async def persisted_users(sample_users_raw_data: list[dict[str, Any]]) -> list[User]:
    """Take raw user data dictionaries and insert User documents into the in-memory database."""
    users = [User(**item) for item in sample_users_raw_data]
    for user in users:
        await user.insert()
    return users


@pytest_asyncio.fixture
async def persisted_user(persisted_users: list[User]) -> User:
    """Convenience fixture providing the first persisted User instance from persisted_users."""
    return persisted_users[0]
