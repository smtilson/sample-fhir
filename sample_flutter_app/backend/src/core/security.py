"""Credential security and password hashing utilities (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Passwords must never be stored in plaintext. This module provides native
    bcrypt hashing and verification.

    By using the `bcrypt` library directly, we avoid the unmaintained `passlib`
    dependency and its incompatibility with bcrypt >= 4.0.0 (recorded in
    [ISSUE-DEP-02]).

Devin re-Cognito:
    In AWS Cognito, you do not manage password hashing or verification yourself.
    When a user signs up, credentials are sent over TLS to Cognito User Pools,
    which securely hashes and stores them using AWS KMS-managed keys. Your backend
    never sees or stores user password hashes.
"""

import bcrypt


def hash_password(raw_password: str) -> str:
    """Hash a plaintext password using bcrypt with a freshly generated salt.

    Args:
        raw_password: The plaintext password string to hash.

    Returns:
        The bcrypt-hashed password string suitable for database persistence.
    """
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(raw_password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plaintext password matches an existing bcrypt hash.

    Args:
        plain_password: The candidate plaintext password.
        hashed_password: The stored bcrypt hash string.

    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
