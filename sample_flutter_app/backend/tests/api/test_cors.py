"""Atomic HTTP integration tests for CORS Middleware (SMP-EP1.5-TK01).

WHY THIS FILE EXISTS:
    Flutter Web (the first frontend platform per [Q-SAMPLE-UI-01]) runs on its
    own origin (e.g. http://localhost:3000). Browsers enforce the Same-Origin
    Policy, so without Cross-Origin Resource Sharing (CORS) headers the browser
    would silently block every request to this backend before it ever reaches
    Flutter code.

    These tests verify the three CORS behaviors that matter for our client:

    1. Preflight: A browser sends `OPTIONS` + `Origin` +
       `Access-Control-Request-Method` before any non-simple request. The
       middleware must answer 200 with `access-control-allow-*` headers.
    2. Actual request: A `GET` carrying an allowed `Origin` header must echo
       that origin back in `access-control-allow-origin`.
    3. Untrusted origin: Requests from origins not in `settings.cors_origins`
       must NOT receive `access-control-allow-origin`, so the browser keeps
       blocking them.

    Each test verifies exactly ONE contract per AGENTS.md atomic testing rules.
"""

from httpx import AsyncClient

# An origin that exists in Settings.cors_origins (src/core/config.py).
ALLOWED_ORIGIN = "http://localhost:3000"

# An origin deliberately absent from Settings.cors_origins.
DISALLOWED_ORIGIN = "http://untrusted-malicious-site.com"


async def test_cors_preflight_allowed_origin_returns_allow_headers(
    client: AsyncClient,
) -> None:
    """OPTIONS preflight from an allowed origin returns 200 and CORS allow headers.

    Simulates exactly what the Flutter Web browser sends before a cross-origin
    request: an OPTIONS call declaring the intended method and headers.
    """
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert "GET" in response.headers["access-control-allow-methods"]


async def test_cors_get_request_allowed_origin_echoes_origin(
    client: AsyncClient,
) -> None:
    """GET with an allowed Origin header receives matching allow-origin header."""
    response = await client.get(
        "/api/v1/health",
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


async def test_cors_disallowed_origin_receives_no_allow_header(
    client: AsyncClient,
) -> None:
    """Request from an untrusted origin must not receive allow-origin headers.

    The endpoint still executes (CORS is a browser-enforced policy, not a
    server-side auth mechanism), but the missing header means a real browser
    would hide the response from JavaScript — preserving the allow-list.
    """
    response = await client.get(
        "/api/v1/health",
        headers={"Origin": DISALLOWED_ORIGIN},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
