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

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI

# Ensure the backend directory is always on sys.path for direct uvicorn execution
backend_root = str(Path(__file__).resolve().parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from src.api.health import router as health_router
from src.api.tasks import router as tasks_router
from src.api.users import router as users_router
from src.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    await init_db()
    yield


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
        lifespan=lifespan,
    )

    # Register routers — one line per feature area.
    app.include_router(health_router)
    app.include_router(users_router)
    app.include_router(tasks_router)

    return app


# ASGI entrypoint consumed by Uvicorn.
app = create_app()
