"""Shared pytest fixtures (SMP-EP0-TK01).

WHY THIS FILE EXISTS:
    `conftest.py` is pytest's conventional location for fixtures that should
    be available to every test in this directory tree — no imports needed in
    the test files themselves.

    The `client` fixture below is the backbone of API-level tests: it builds
    a fresh FastAPI app via `create_app()` and wraps it in an httpx
    `AsyncClient` that talks to the app *in-process* through ASGITransport.

    That means:
      - No real HTTP server, no sockets, no ports — fast and hermetic.
      - Each test gets its own app instance (function-scoped), so there is
        no cross-test state.
      - It exercises the full ASGI stack (routing, serialization, error
        handling), giving near-integration fidelity at unit-test cost.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import create_app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an async HTTP client bound to a freshly built app instance.

    Function scope (the default) is intentional: every test gets a clean app.
    `base_url` is a placeholder — ASGITransport never hits the network, but
    httpx requires an absolute URL to build requests.
    """
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
