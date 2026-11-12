"""Unit tests for cryptographic security utilities (SMP-EP1-TK01).

WHY THIS FILE EXISTS:
    Validates credential hashing logic in isolation without requiring database
    access or HTTP server fixtures:
    1. Passwords are never returned or stored as plaintext.
    2. Bcrypt salts are uniquely generated per hashing invocation (non-deterministic).
    3. Hashes conform to standard modular crypt format ($2a$, $2b$, or $2y$).
    4. verify_password accurately distinguishes correct and incorrect passwords.
"""

from src.core.security import hash_password, verify_password


def test_hash_password_generates_valid_salted_bcrypt_hash() -> None:
    """Verifies that hash_password creates non-plaintext salted bcrypt hashes."""
    raw_password = "SecurePassword123!"

    hashed = hash_password(raw_password)

    # 1. Password must not be plaintext
    assert hashed != raw_password

    # 2. Bcrypt hash format check ($2a$, $2b$, or $2y$)
    assert hashed.startswith("$2")

    # 3. Two successive calls on the same plaintext must produce different hashes (unique salts)
    second_hash = hash_password(raw_password)
    assert hashed != second_hash


def test_verify_password_matches_correct_and_rejects_incorrect() -> None:
    """Verifies that verify_password correctly authenticates against the bcrypt hash."""
    raw_password = "CorrectHorseBatteryStaple"
    hashed = hash_password(raw_password)

    # Positive match
    assert verify_password(raw_password, hashed) is True

    # Rejection of wrong password
    assert verify_password("WrongPassword123", hashed) is False

    # Rejection of empty password
    assert verify_password("", hashed) is False
