"""Atomic unit tests for Task Transport Schemas (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Validates Pydantic schemas (`TaskCreate`, `TaskUpdate`, `TaskOut`) in complete
    isolation from database drivers and HTTP transports:
    1. Input validation constraints: non-empty name, required user_id, default values.
    2. Partial update schema: all fields optional, min_length validation.
    3. Output schema contracts: from_attributes mapping, public field validation.
"""

from typing import Any
import pytest
from pydantic import ValidationError

from src.schemas.task import TaskCreate, TaskOut, TaskUpdate


# --- 1. TaskCreate Schema Tests ---

def test_task_create_schema_valid_data() -> None:
    """Verifies that valid data instantiates TaskCreate with matching field values."""
    payload = {
        "user_id": "654321654321654321654321",
        "name": "Design system architecture",
        "is_completed": True,
        "metadata": {"tags": ["architecture", "planning"]},
    }

    schema = TaskCreate(**payload)

    assert schema.user_id == "654321654321654321654321"
    assert schema.name == "Design system architecture"
    assert schema.is_completed is True
    assert schema.metadata == {"tags": ["architecture", "planning"]}


def test_task_create_schema_default_values() -> None:
    """Verifies default values: is_completed is False and metadata is empty dict."""
    schema = TaskCreate(
        user_id="654321654321654321654321",
        name="Task with Defaults",
    )

    assert schema.is_completed is False
    assert schema.metadata == {}


def test_task_create_schema_empty_name_raises_validation_error() -> None:
    """Verifies that empty string names fail the min_length=1 constraint."""
    with pytest.raises(ValidationError):
        TaskCreate(user_id="123", name="")


def test_task_create_schema_missing_name_raises_validation_error() -> None:
    """Verifies that TaskCreate rejects payloads missing the required name field."""
    with pytest.raises(ValidationError):
        TaskCreate(user_id="123")  # type: ignore[call-arg]


def test_task_create_schema_missing_user_id_raises_validation_error() -> None:
    """Verifies that TaskCreate rejects payloads missing the required user_id field."""
    with pytest.raises(ValidationError):
        TaskCreate(name="Task Title")  # type: ignore[call-arg]


# --- 2. TaskUpdate Schema Tests ---

def test_task_update_schema_all_fields_optional() -> None:
    """Verifies that TaskUpdate can be instantiated with no arguments."""
    update = TaskUpdate()

    assert update.name is None
    assert update.is_completed is None
    assert update.metadata is None


def test_task_update_schema_accepts_partial_data() -> None:
    """Verifies that TaskUpdate accepts partial field updates."""
    # Updating only is_completed
    update_status = TaskUpdate(is_completed=True)
    assert update_status.is_completed is True
    assert update_status.name is None

    # Updating only name
    update_name = TaskUpdate(name="New Name")
    assert update_name.name == "New Name"
    assert update_name.is_completed is None

    # Updating only metadata
    update_meta = TaskUpdate(metadata={"priority": "low"})
    assert update_meta.metadata == {"priority": "low"}


def test_task_update_schema_empty_name_raises_validation_error() -> None:
    """Verifies that TaskUpdate rejects an empty string name if provided."""
    with pytest.raises(ValidationError):
        TaskUpdate(name="")


# --- 3. TaskOut Public Contract Tests ---

def test_task_out_schema_instantiation_from_dict() -> None:
    """Verifies that valid data instantiates TaskOut with exact public fields."""
    payload = {
        "id": "111111111111111111111111",
        "user_id": "222222222222222222222222",
        "name": "Public Task",
        "is_completed": False,
        "metadata": {"source": "web"},
    }

    task_out = TaskOut(**payload)

    assert task_out.id == "111111111111111111111111"
    assert task_out.user_id == "222222222222222222222222"
    assert task_out.name == "Public Task"
    assert task_out.is_completed is False
    assert task_out.metadata == {"source": "web"}


def test_task_out_schema_maps_from_attributes() -> None:
    """Verifies that TaskOut correctly populates from object attributes (from_attributes=True)."""
    class MockTaskEntity:
        id = "333333333333333333333333"
        user_id = "444444444444444444444444"
        name = "Mapped Task"
        is_completed = True
        metadata = {"due": "tomorrow"}

    task_out = TaskOut.model_validate(MockTaskEntity(), from_attributes=True)

    assert task_out.id == "333333333333333333333333"
    assert task_out.user_id == "444444444444444444444444"
    assert task_out.name == "Mapped Task"
    assert task_out.is_completed is True
    assert task_out.metadata == {"due": "tomorrow"}


def test_task_out_schema_missing_id_raises_validation_error() -> None:
    """Verifies that TaskOut requires the id field."""
    with pytest.raises(ValidationError):
        TaskOut(user_id="1", name="Task", is_completed=False)  # type: ignore[call-arg]


def test_task_out_schema_missing_user_id_raises_validation_error() -> None:
    """Verifies that TaskOut requires the user_id field."""
    with pytest.raises(ValidationError):
        TaskOut(id="1", name="Task", is_completed=False)  # type: ignore[call-arg]
