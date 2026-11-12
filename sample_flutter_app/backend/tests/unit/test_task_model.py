"""Atomic document-level CRUD and database constraint unit tests for Task (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Validates the `Task` Beanie document model directly against the database
    with single-responsibility, atomic unit tests:
    - Each test verifies exactly ONE operation, default value, or failure mode.
    - Tests consume layered fixtures (`sample_tasks_raw_data`, `persisted_task`).
    - Zero dependencies on HTTP routes or FastAPI middleware.
"""

from typing import Any
from bson import ObjectId
import pytest
from pydantic import ValidationError

from src.models.task import Task
from src.models.user import User


# --- 1. Creation & Default Values Tests ---

async def test_task_document_create_assigns_id_and_persists(
    sample_tasks_raw_data: list[dict[str, Any]],
) -> None:
    """Verifies that inserting a valid Task document assigns an ObjectId and increments count."""
    raw_data = sample_tasks_raw_data[0]
    task = Task(**raw_data)

    assert task.id is None
    await task.insert()

    assert task.id is not None
    assert await Task.count() == 1


async def test_task_document_default_values(persisted_user: User) -> None:
    """Verifies that is_completed defaults to False and metadata defaults to empty dict."""
    task = Task(user_id=str(persisted_user.id), name="Default Check Task")
    await task.insert()

    assert task.is_completed is False
    assert task.metadata == {}


# --- 2. Read / Query Tests ---

async def test_task_document_read_by_id(persisted_task: Task) -> None:
    """Verifies reading an existing task document by its MongoDB ObjectId."""
    found = await Task.get(persisted_task.id)

    assert found is not None
    assert found.id == persisted_task.id
    assert found.name == persisted_task.name
    assert found.user_id == persisted_task.user_id


async def test_task_document_read_by_user_id(
    persisted_task: Task,
    persisted_user: User,
) -> None:
    """Verifies querying tasks scoped to a specific user_id."""
    user_tasks = await Task.find(Task.user_id == str(persisted_user.id)).to_list()

    assert len(user_tasks) >= 1
    task_ids = [t.id for t in user_tasks]
    assert persisted_task.id in task_ids


async def test_task_document_read_nonexistent_id_returns_none() -> None:
    """Verifies that querying an unknown ObjectId returns None without raising an error."""
    nonexistent_id = ObjectId()
    found = await Task.get(nonexistent_id)

    assert found is None


# --- 3. Schema / Field Validation Tests ---

def test_task_document_missing_user_id_raises_validation_error() -> None:
    """Verifies that Pydantic/Beanie rejects model instantiation when user_id is omitted."""
    with pytest.raises(ValidationError):
        Task(name="Task Without User")  # type: ignore[call-arg]


def test_task_document_missing_name_raises_validation_error(persisted_user: User) -> None:
    """Verifies that Pydantic/Beanie rejects model instantiation when name is omitted."""
    with pytest.raises(ValidationError):
        Task(user_id=str(persisted_user.id))  # type: ignore[call-arg]


# --- 4. Update Tests ---

async def test_task_document_update_name_modifies_persisted_field(
    persisted_task: Task,
) -> None:
    """Verifies updating an existing task's name via Beanie set operator."""
    await persisted_task.set({Task.name: "Updated Task Title"})

    refreshed = await Task.get(persisted_task.id)
    assert refreshed is not None
    assert refreshed.name == "Updated Task Title"


async def test_task_document_update_completion_status(
    persisted_task: Task,
) -> None:
    """Verifies toggling is_completed via Beanie set operator."""
    new_status = not persisted_task.is_completed
    await persisted_task.set({Task.is_completed: new_status})

    refreshed = await Task.get(persisted_task.id)
    assert refreshed is not None
    assert refreshed.is_completed == new_status


async def test_task_document_update_metadata(
    persisted_task: Task,
) -> None:
    """Verifies updating metadata dictionary via Beanie set operator."""
    new_meta = {"priority": "critical", "estimated_minutes": 45}
    await persisted_task.set({Task.metadata: new_meta})

    refreshed = await Task.get(persisted_task.id)
    assert refreshed is not None
    assert refreshed.metadata == new_meta


# --- 5. Delete Tests ---

async def test_task_document_delete_removes_from_database(
    persisted_task: Task,
) -> None:
    """Verifies deleting an existing task document removes it from the database."""
    task_id = persisted_task.id

    await persisted_task.delete()

    deleted = await Task.get(task_id)
    assert deleted is None


# --- 6. Collection Configuration Tests ---

def test_task_document_collection_name() -> None:
    """Verifies that Task document maps to the 'tasks' collection."""
    assert Task.get_settings().name == "tasks"
