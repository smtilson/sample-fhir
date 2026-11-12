"""User transport schemas (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Pydantic schemas define the data contract for HTTP requests and responses.
    Decoupling schemas from Beanie document models prevents leaking internal
    database details (most critically, the bcrypt password hash is omitted
    from UserOut so it can never be exposed in API responses).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for creating a new user account."""

    name: str = Field(..., min_length=1, description="Display name of the user")
    email: EmailStr = Field(..., description="Unique email address for the account")
    password: str = Field(..., min_length=4, description="User password")


class UserOut(BaseModel):
    """Public representation of a user account returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique database identifier (hex string)")
    name: str = Field(..., description="Display name of the user")
    email: str = Field(..., description="User email address")
