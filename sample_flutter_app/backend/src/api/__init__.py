"""API routers package.

WHY THIS FILE EXISTS:
    Marks `src/api/` as a Python package. All HTTP route modules (health,
    tasks, auth, exports, ...) live here as `APIRouter` instances and are
    registered on the app in `src/main.py`. Grouping routers in one package
    keeps the transport layer separated from domain logic, per the
    ports-and-adapters architecture decision.
"""
