"""Application configuration settings (SMP-EP1-TK05).

WHY THIS FILE EXISTS:
    Centralizes environment settings using Pydantic Settings (PEP 621 / Pydantic v2).
    - app_env: "demo" (default for local probing), "test", or "production".
    - database_url: "memory" (default for in-memory mongomock), or a MongoDB/DocumentDB URI.
    - database_name: Target database namespace.

Devin re-Cognito:
    In AWS production, `database_url` is provided via AWS Systems Manager
    Parameter Store or Secrets Manager, pointing to an Amazon DocumentDB cluster
    with TLS enabled (e.g. `mongodb://<user>:<pwd>@<docdb-cluster>:27017/?tls=true`).
    The local "memory" mode is an ergonomic testing double.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration parsed from environment variables or .env file."""

    app_env: str = "demo"
    database_url: str = "memory"
    database_name: str = "sample_todo_db"
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
