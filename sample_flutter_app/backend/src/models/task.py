"""Task Document model (SMP-EP1-TK04).

WHY THIS FILE EXISTS:
    Defines the persistence model for user-scoped tasks using Beanie ODM over
    MongoDB / Amazon DocumentDB.
    Per decision [Q-SAMPLE-REORG-01], this model is kept intentionally simple
    (user_id, name, is_completed, metadata) to prioritize rapid development
    and live synchronization with the Flutter frontend.

Devin re-Cognito:
    In AWS Cognito, tasks link to users via the Cognito `sub` (a UUID string
    assigned to the user upon registration). The `user_id` field here holds that
    exact identifier. No foreign key constraints exist in MongoDB, making it
    directly compatible with Cognito without needing a local users table.
"""

from typing import Any
from beanie import Document, Indexed
from pydantic import Field


class Task(Document):
    """Task document scoped to a specific user account."""

    user_id: Indexed(str)
    name: str
    is_completed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "tasks"
