"""Database initialization and demo data seeding (SMP-EP1-TK05).

WHY THIS FILE EXISTS:
    Configures database connections and model initialization for the application lifecycle:
    - Demo / Memory mode: Uses in-memory `mongomock-motor` so the app can be probed
      immediately via Postman or Swagger UI without a running MongoDB server.
    - Production mode: Connects to real MongoDB / Amazon DocumentDB via Motor.
    - Seeding: Pre-populates sample users and tasks when running in demo mode.

Devin re-Cognito:
    In AWS cloud deployment, Beanie connects via TLS to Amazon DocumentDB, and
    authentication is handled by AWS Cognito. In demo mode, sample users are pre-seeded
    with bcrypt hashes so endpoints can be exercised offline.
"""

from typing import Any
import mongomock.database
import mongomock_motor
from beanie import init_beanie

from src.core.config import settings
from src.core.security import hash_password
from src.models.task import Task
from src.models.user import User

# TODO: Add logging
# TODO: This isn't modular enough, there isn't enough separation of concerns

# -----------------------------------------------------------------------------
# Upstream Compatibility Shim [ISSUE-DEP-03]:
# NOTE: This is a temporary monkeypatch for an upstream library incompatibility,
# tracked in docs/PENDING_ISSUES_AND_QUESTIONS.md [ISSUE-DEP-03].
# Beanie 1.25+ passes `authorizedCollections=True` and `nameOnly=True` to
# `list_collection_names()`. mongomock has not updated its signature to accept
# these server-hint kwargs, causing a TypeError during `init_beanie()`.
# TODO: This needs to be further addressed — centralize into a single utility
# or remove once upstream mongomock/mongomock-motor resolves keyword handling.
# -----------------------------------------------------------------------------
_orig_list_collection_names = mongomock.database.Database.list_collection_names


def _patched_list_collection_names(self: Any, *args: Any, **kwargs: Any) -> list[str]:
    kwargs.pop("authorizedCollections", None)
    kwargs.pop("nameOnly", None)
    return _orig_list_collection_names(self, *args, **kwargs)


mongomock.database.Database.list_collection_names = _patched_list_collection_names


async def seed_demo_data() -> None:
    """Pre-seed sample users and tasks if the database is currently empty."""
    user_count = await User.count()
    if user_count > 0:
        return

    # 1. Create Demo Users
    alice = User(
        name="Alice Smith",
        email="alice@example.com",
        password=hash_password("password123"),
    )
    await alice.insert()

    bob = User(
        name="Bob Jones",
        email="bob@example.com",
        password=hash_password("password123"),
    )
    await bob.insert()

    # 2. Create Demo Tasks for Alice
    alice_id = str(alice.id)
    await Task(
        user_id=alice_id,
        name="Explore FastAPI Swagger documentation at /docs",
        is_completed=True,
        metadata={"priority": "high", "category": "demo"},
    ).insert()

    await Task(
        user_id=alice_id,
        name="Probe endpoints using Postman or curl",
        is_completed=False,
        metadata={"priority": "urgent"},
    ).insert()

    await Task(
        user_id=alice_id,
        name="Connect Flutter frontend client",
        is_completed=False,
        metadata={"category": "flutter"},
    ).insert()

    # 3. Create Demo Task for Bob
    bob_id = str(bob.id)
    await Task(
        user_id=bob_id,
        name="Review FHIR task alignment and roadmap",
        is_completed=False,
        metadata={"priority": "routine"},
    ).insert()


async def init_db() -> None:
    """Initialize Beanie ODM with either in-memory mock or real MongoDB client."""
    is_memory = settings.database_url == "memory" or settings.app_env == "demo"

    if is_memory:
        client = mongomock_motor.AsyncMongoMockClient()
        db = client[settings.database_name]
    else:
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.database_url)
        db = client[settings.database_name]

    await init_beanie(
        database=db,
        document_models=[User, Task],
    )

    if settings.app_env == "demo":
        await seed_demo_data()
