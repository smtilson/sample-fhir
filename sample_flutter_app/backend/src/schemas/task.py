"""Task transport schemas (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Pydantic schemas define the data contract for Task HTTP requests and responses.
    - TaskCreate: Validates payload when creating a new task scoped to a user.
    - TaskUpdate: Validates partial updates (e.g. toggling is_completed or updating metadata).
    - TaskOut: Public representation of a task returned by API endpoints.
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Payload for creating a new user-scoped task."""

    user_id: str = Field(..., description="ID of the user who owns this task")
    name: str = Field(..., min_length=1, description="Title or name of the task")
    is_completed: bool = Field(False, description="Initial completion status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom key-value attributes")


class TaskUpdate(BaseModel):
    """Payload for updating an existing task (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, description="Updated task name")
    is_completed: Optional[bool] = Field(None, description="Updated completion status")
    metadata: Optional[dict[str, Any]] = Field(None, description="Updated metadata dictionary")


class TaskOut(BaseModel):
    """Public representation of a task returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique database identifier (hex string)")
    user_id: str = Field(..., description="ID of the user who owns this task")
    name: str = Field(..., description="Title or name of the task")
    is_completed: bool = Field(..., description="Completion status")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata attributes")
