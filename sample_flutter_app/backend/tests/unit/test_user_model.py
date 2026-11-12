"""Atomic document-level CRUD and database constraint unit tests (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Validates the `User` Beanie document model directly against the database
    with single-responsibility, atomic unit tests:
    - Each test verifies exactly ONE operation or failure mode.
    - Tests that require pre-existing data consume the `persisted_user` or
      `persisted_users` fixtures rather than performing inline setup.
    - Zero dependencies on HTTP routes or FastAPI middleware.
"""

from typing import Any
from bson import ObjectId
import pymongo.errors
import pytest
from pydantic import ValidationError

from src.models.user import User


# --- 1. Creation Tests ---

async def test_user_document_create_assigns_id_and_persists(
    sample_users_raw_data: list[dict[str, Any]],
) -> None:
    """Verifies that inserting a valid User document assigns an ObjectId and increments count."""
    raw_data = sample_users_raw_data[0]
    user = User(**raw_data)

    assert user.id is None
    
    await user.insert()

    assert user.id is not None
    assert await User.count() == 1


# --- 2. Read / Query Tests ---

async def test_user_document_read_by_id(persisted_user: User) -> None:
    """Verifies reading an existing user document by its MongoDB ObjectId."""
    found = await User.get(persisted_user.id)

    assert found is not None
    assert found.id == persisted_user.id
    assert found.email == persisted_user.email
    assert found.name == persisted_user.name


async def test_user_document_read_by_email(persisted_user: User) -> None:
    """Verifies querying an existing user document by unique email index."""
    found = await User.find_one(User.email == persisted_user.email)

    assert found is not None
    assert found.id == persisted_user.id


async def test_user_document_read_nonexistent_id_returns_none() -> None:
    """Verifies that querying an unknown ObjectId returns None without raising an error."""
    nonexistent_id = ObjectId()
    found = await User.get(nonexistent_id)

    assert found is None


async def test_user_document_read_nonexistent_email_returns_none() -> None:
    """Verifies that querying an unregistered email address returns None."""
    found = await User.find_one(User.email == "nonexistent_email@example.com")

    assert found is None


# --- 3. Database Constraint Tests ---

async def test_user_document_duplicate_email_raises_duplicate_key_error(
    persisted_user: User,
) -> None:
    """Verifies that attempting to insert a duplicate email raises DuplicateKeyError from MongoDB."""
    duplicate_user = User(
        name="Duplicate Imposter",
        email=persisted_user.email,
        password="different_hashed_password",
    )

    with pytest.raises(pymongo.errors.DuplicateKeyError):
        await duplicate_user.insert()


# --- 4. Schema / Field Validation Tests ---

def test_user_document_missing_email_raises_validation_error() -> None:
    """Verifies that Pydantic/Beanie rejects model instantiation when email is omitted."""
    with pytest.raises(ValidationError):
        User(name="No Email", password="somepassword")  # type: ignore[call-arg]


def test_user_document_missing_password_raises_validation_error() -> None:
    """Verifies that Pydantic/Beanie rejects model instantiation when password is omitted."""
    with pytest.raises(ValidationError):
        User(name="No Password", email="valid@example.com")  # type: ignore[call-arg]


def test_user_document_missing_name_raises_validation_error() -> None:
    """Verifies that Pydantic/Beanie rejects model instantiation when name is omitted."""
    with pytest.raises(ValidationError):
        User(email="valid@example.com", password="somepassword")  # type: ignore[call-arg]


# --- 5. Update Tests ---

async def test_user_document_update_modifies_persisted_fields(
    persisted_user: User,
) -> None:
    """Verifies updating an existing user's fields via Beanie ODM set operator."""
    await persisted_user.set({User.name: "Updated Name"})

    refreshed = await User.get(persisted_user.id)
    assert refreshed is not None
    assert refreshed.name == "Updated Name"


# --- 6. Delete Tests ---

async def test_user_document_delete_removes_from_database(
    persisted_user: User,
) -> None:
    """Verifies deleting an existing user document removes it from the database."""
    user_id = persisted_user.id

    await persisted_user.delete()

    deleted = await User.get(user_id)
    assert deleted is None
    # Count is 2 now because the db starts with 3 users.
    assert await User.count() == 2
