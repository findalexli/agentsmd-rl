"""Behavioral checks for prefect-update-agentsmd-files-for-f2e4715 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert '- On init, stored credentials are validated against `/admin/version` with a `Basic` auth header. Invalid credentials are cleared immediately. A persistent error toast is shown **only on 401** — networ' in text, "expected to find: " + '- On init, stored credentials are validated against `/admin/version` with a `Basic` auth header. Invalid credentials are cleared immediately. A persistent error toast is shown **only on 401** — networ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert '- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` and show a persistent err' in text, "expected to find: " + '- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` and show a persistent err'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert '- Auth failure toasts use `id: "auth-failed"` (via `sonner`) for deduplication — multiple rapid auth failures produce only one visible toast.' in text, "expected to find: " + '- Auth failure toasts use `id: "auth-failed"` (via `sonner`) for deduplication — multiple rapid auth failures produce only one visible toast.'[:80]

