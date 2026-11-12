"""TDD test for the health check endpoint (SMP-EP0-TK01).

WHY THIS FILE EXISTS:
    Ticket acceptance criteria: `pytest tests/api/test_health.py` must assert
    that `GET /api/v1/health` returns HTTP 200 and `{"status": "ok"}`.

    This test uses the `client` fixture from `tests/conftest.py`, which is
    injected by parameter name — pytest resolves it automatically.

    NOTE: No `@pytest.mark.asyncio` decorator is needed because
    `asyncio_mode = "auto"` is set in pyproject.toml — pytest-asyncio picks
    up `async def` tests automatically.
"""

from httpx import AsyncClient


async def test_health_returns_200_and_ok_status(client: AsyncClient) -> None:
    """GET /api/v1/health must return 200 with {"status": "ok"} JSON."""
    response = await client.get("/api/v1/health")

    # 1) Transport contract: the endpoint exists and succeeds.
    assert response.status_code == 200

    # 2) Payload contract: exact body, not just "contains status" — catches
    #    accidental extra fields or changed values.
    assert response.json() == {"status": "ok"}
