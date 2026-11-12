"""Task CRUD API router (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Provides HTTP REST endpoints for the complete Task lifecycle:
    - POST /api/v1/tasks: Creates a task linked to an existing user.
    - GET /api/v1/tasks: Lists tasks, optionally filtered by ?user_id=...
    - GET /api/v1/tasks/{task_id}: Retrieves a single task by ID.
    - PATCH /api/v1/tasks/{task_id}: Updates fields (toggle is_completed, update name/metadata).
    - DELETE /api/v1/tasks/{task_id}: Removes a task by ID.

Devin re-Cognito:
    In AWS Cognito, tasks link to the authenticated user's Cognito `sub` UUID.
    When auth is enabled in Epoch 3, the `user_id` will be automatically extracted
    from the verified JWT claims rather than manually supplied in the body.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.models.task import Task
from src.models.user import User
from src.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(task_in: TaskCreate) -> TaskOut:
    """Create a task scoped to an existing user."""
    # Verify that the referenced user exists
    try:
        user = await User.get(task_in.user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )

    task = Task(
        user_id=task_in.user_id,
        name=task_in.name,
        is_completed=task_in.is_completed,
        metadata=task_in.metadata,
    )
    await task.insert()

    return TaskOut(
        id=str(task.id),
        user_id=task.user_id,
        name=task.name,
        is_completed=task.is_completed,
        metadata=task.metadata,
    )


@router.get(
    "",
    response_model=list[TaskOut],
    summary="List tasks",
)
async def list_tasks(
    user_id: Optional[str] = Query(None, description="Filter tasks by user ID"),
) -> list[TaskOut]:
    """Retrieve all tasks, optionally scoped to a specific user_id."""
    if user_id:
        tasks = await Task.find(Task.user_id == user_id).to_list()
    else:
        tasks = await Task.find_all().to_list()

    return [
        TaskOut(
            id=str(t.id),
            user_id=t.user_id,
            name=t.name,
            is_completed=t.is_completed,
            metadata=t.metadata,
        )
        for t in tasks
    ]


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    summary="Get task by ID",
)
async def get_task(task_id: str) -> TaskOut:
    """Retrieve a single task by its database identifier."""
    try:
        task = await Task.get(task_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskOut(
        id=str(task.id),
        user_id=task.user_id,
        name=task.name,
        is_completed=task.is_completed,
        metadata=task.metadata,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
    summary="Update task",
)
async def update_task(task_id: str, task_in: TaskUpdate) -> TaskOut:
    """Update fields on an existing task (name, is_completed, metadata)."""
    try:
        task = await Task.get(task_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task_in.name is not None:
        task.name = task_in.name

    if task_in.is_completed is not None:
        task.is_completed = task_in.is_completed

    if task_in.metadata is not None:
        task.metadata = task_in.metadata

    await task.save()

    return TaskOut(
        id=str(task.id),
        user_id=task.user_id,
        name=task.name,
        is_completed=task.is_completed,
        metadata=task.metadata,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
async def delete_task(task_id: str) -> None:
    """Delete a task by its database identifier."""
    try:
        task = await Task.get(task_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await task.delete()
