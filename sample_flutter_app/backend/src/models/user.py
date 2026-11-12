"""User Document model (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Defines the persistence model for accounts using Beanie ODM over MongoDB.
    Per decision [Q-SAMPLE-REORG-01], this model is kept intentionally minimal
    (name, email, password) to fast-track learning Flutter and establishing
    frontend-backend sync before introducing complex authentication tokens.

Devin re-Cognito:
    In AWS Cognito, user identities live in a Cognito User Pool rather than an
    application database collection. Cognito issues a unique `sub` (UUID) upon
    registration. In a full AWS architecture, your application database never has
    a `users` collection with passwords; tasks simply reference the user's
    Cognito `sub` directly.
"""

from beanie import Document, Indexed


class User(Document):
    """User account document in MongoDB / Amazon DocumentDB."""

    name: str
    email: Indexed(str, unique=True)
    password: str  # Stored exclusively as a bcrypt hash

    class Settings:
        name = "users"
