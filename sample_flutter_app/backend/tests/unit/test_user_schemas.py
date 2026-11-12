"""Atomic unit tests for User Transport Schemas (SMP-EP1-TK02).

WHY THIS FILE EXISTS:
    Validates Pydantic schemas (`UserCreate`, `UserOut`) in complete isolation
    from database drivers and HTTP transports:
    1. Input validation constraints: email syntax formatting, minimum string lengths.
    2. Attribute mapping: converting domain objects into public DTO representations.
    3. Credential shielding: verifying that output schemas never expose password fields.
"""

from typing import Any
import pytest
from pydantic import ValidationError

from src.schemas.user import UserCreate, UserOut, UserUpdate


# --- 1. UserCreate Schema Tests ---

def test_user_create_schema_valid_data() -> None:
    """Verifies that a valid dictionary instantiates UserCreate with correct field values."""
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "SecurePassword123",
    }

    user_create = UserCreate(**payload)

    assert user_create.name == "Alice Smith"
    assert user_create.email == "alice@example.com"
    assert user_create.password == "SecurePassword123"


@pytest.mark.parametrize(
    "invalid_email",
    [
        "notanemail",
        "missingdomain@",
        "@missinguser.com",
        "spaces in@example.com",
        "missingatsign.com",
    ],
)
def test_user_create_schema_invalid_email_format_raises_validation_error(
    invalid_email: str,
) -> None:
    """Verifies that EmailStr rejects malformed email strings."""
    with pytest.raises(ValidationError):
        UserCreate(name="Valid Name", email=invalid_email, password="password123")  # type: ignore[arg-type]


def test_user_create_schema_missing_email_raises_validation_error() -> None:
    """Verifies that UserCreate rejects payloads missing the required email field."""
    with pytest.raises(ValidationError):
        UserCreate(name="Alice", password="password123")  # type: ignore[call-arg]


def test_user_create_schema_empty_name_raises_validation_error() -> None:
    """Verifies that empty string names fail the min_length=1 constraint."""
    with pytest.raises(ValidationError):
        UserCreate(name="", email="alice@example.com", password="password123")


def test_user_create_schema_missing_name_raises_validation_error() -> None:
    """Verifies that UserCreate rejects payloads missing the required name field."""
    with pytest.raises(ValidationError):
        UserCreate(email="alice@example.com", password="password123")  # type: ignore[call-arg]


def test_user_create_schema_short_password_raises_validation_error() -> None:
    """Verifies that passwords shorter than 4 characters fail the min_length=4 constraint."""
    with pytest.raises(ValidationError):
        UserCreate(name="Alice", email="alice@example.com", password="123")


def test_user_create_schema_missing_password_raises_validation_error() -> None:
    """Verifies that UserCreate rejects payloads missing the required password field."""
    with pytest.raises(ValidationError):
        UserCreate(name="Alice", email="alice@example.com")  # type: ignore[call-arg]


# --- 2. UserUpdate Schema Tests ---

def test_user_update_schema_all_fields_optional() -> None:
    """Verifies that UserUpdate can be instantiated with no fields provided."""
    update = UserUpdate()
    assert update.name is None
    assert update.email is None
    assert update.password is None


def test_user_update_schema_accepts_partial_data() -> None:
    """Verifies that UserUpdate accepts a subset of fields."""
    update = UserUpdate(name="Updated Name")
    assert update.name == "Updated Name"
    assert update.email is None
    assert update.password is None


def test_user_update_schema_invalid_email_raises_validation_error() -> None:
    """Verifies that UserUpdate rejects malformed email strings."""
    with pytest.raises(ValidationError):
        UserUpdate(email="notanemail")  # type: ignore[arg-type]


def test_user_update_schema_short_password_raises_validation_error() -> None:
    """Verifies that UserUpdate rejects passwords shorter than 4 characters."""
    with pytest.raises(ValidationError):
        UserUpdate(password="12")


def test_user_update_schema_empty_name_raises_validation_error() -> None:
    """Verifies that UserUpdate rejects empty string names."""
    with pytest.raises(ValidationError):
        UserUpdate(name="")


# --- 3. UserOut Public Contract & Credential Shielding Tests ---

def test_user_out_schema_instantiation_from_dict() -> None:
    """Verifies that valid data instantiates UserOut with exact public fields."""
    payload = {
        "id": "654321654321654321654321",
        "name": "Bob Jones",
        "email": "bob@example.com",
    }

    user_out = UserOut(**payload)

    assert user_out.id == "654321654321654321654321"
    assert user_out.name == "Bob Jones"
    assert user_out.email == "bob@example.com"


def test_user_out_schema_maps_from_attributes() -> None:
    """Verifies that UserOut correctly populates from object attributes (from_attributes=True)."""
    # why is this being defined here as opposed to in a fixture?
    class MockUserEntity:
        id = "654321654321654321654321"
        name = "Charlie Brown"
        email = "charlie@example.com"
        password = "secret_hashed_password"

    user_out = UserOut.model_validate(MockUserEntity(), from_attributes=True)

    assert user_out.id == "654321654321654321654321"
    assert user_out.name == "Charlie Brown"
    assert user_out.email == "charlie@example.com"


def test_user_out_schema_missing_id_raises_validation_error() -> None:
    """Verifies that UserOut requires the id field."""
    with pytest.raises(ValidationError):
        UserOut(name="Bob", email="bob@example.com")  # type: ignore[call-arg]


def test_user_out_schema_does_not_contain_password_fields() -> None:
    """CRITICAL: Verifies that UserOut schema definition has zero password attributes."""
    field_names = set(UserOut.model_fields.keys())

    assert "password" not in field_names
    assert "hashed_password" not in field_names
    assert field_names == {"id", "name", "email"}


def test_user_out_schema_dump_never_exposes_password() -> None:
    """CRITICAL: Verifies that serializing UserOut produces no credential keys."""
    user_out = UserOut(
        id="12345",
        name="Dave",
        email="dave@example.com",
    )

    dumped = user_out.model_dump()

    assert "password" not in dumped
    assert "hashed_password" not in dumped
    assert dumped == {"id": "12345", "name": "Dave", "email": "dave@example.com"}
