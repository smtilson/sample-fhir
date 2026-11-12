"""Health check router (SMP-EP0-TK01).

WHY THIS FILE EXISTS:
    Provides a liveness/readiness probe endpoint. Health checks are required
    by load balancers, container orchestrators (ECS/Kubernetes), and uptime
    monitors — including the AWS deployment path planned for this project.

    It is implemented as an `APIRouter` (not registered directly on the app)
    so that the transport surface stays modular: each feature area gets its
    own router file, and `src/main.py` composes them. This is the pattern
    every future route module (tasks, auth, exports) will follow.
"""

from fastapi import APIRouter

# `prefix` is baked in here so the router is self-describing; main.py simply
# includes it without needing to know the versioned path.
router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a static liveness payload.

    Deliberately has no dependencies (no DB, no settings) so it stays a pure
    "is the process up" signal. A deeper readiness check that pings MongoDB
    can be added later as a separate endpoint if needed.
    """
    return {"status": "ok"}
