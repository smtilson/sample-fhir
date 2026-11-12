"""Test suite root package.

WHY THIS FILE EXISTS:
    Marks `tests/` as a package so test modules can be imported consistently
    and so `tests/api/` (a subpackage) resolves cleanly under pytest's
    rootdir-based collection. It intentionally contains no code — all shared
    fixtures live in `tests/conftest.py`.
"""
