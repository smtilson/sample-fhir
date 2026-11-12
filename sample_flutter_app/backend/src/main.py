"""FastAPI application entrypoint (SMP-EP0-TK01).

WHY THIS FILE EXISTS:
    Defines `create_app()`, an *application factory*. Using a factory instead
    of instantiating `FastAPI` at module scope matters because:

      1. Tests can build a fresh, isolated app per fixture — no shared state
         leaks between tests.
      2. Startup wiring (Beanie init, settings, CORS, auth) can be injected
         per-environment later without changing call sites.

    `app = create_app()` at the bottom is what Uvicorn loads:
        uvicorn src.main:app --reload
"""

from fastapi import FastAPI

from src.api.health import router as health_router
from src.api.tasks import router as tasks_router
from src.api.users import router as users_router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    All routers, middleware, and lifecycle hooks get registered here. Keeping
    this function small and declarative makes the app's wiring easy to audit.
    """
    app = FastAPI(
        title="Sample Todo API",
        version="0.1.0",
        description=(
            "FastAPI + Beanie backend for the sample task manager. "
            "Domain models will align incrementally with FHIR Task concepts."
        ),
    )

    # Register routers — one line per feature area.
    app.include_router(health_router)
    app.include_router(users_router)
    app.include_router(tasks_router)

    return app


# ASGI entrypoint consumed by Uvicorn.
app = create_app()
