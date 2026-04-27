"""Behavioral checks for prefect-update-agentsmd-files-for-0939cd0 (markdown_authoring task).

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
    text = _read('ui-v2/AGENTS.md')
    assert '│   ├── auth/          # Authentication state, AuthProvider, useAuth hook' in text, "expected to find: " + '│   ├── auth/          # Authentication state, AuthProvider, useAuth hook'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert '- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` without a page reload.' in text, "expected to find: " + '- Session invalidation is event-driven: API middleware dispatches a `"auth:unauthorized"` window event, which `AuthProvider` listens for to reset `isAuthenticated` to `false` without a page reload.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert 'Provides the `AuthProvider` component and `useAuth` hook that gate access to the UI when the server requires authentication. Handles credential storage, validation, and session invalidation.' in text, "expected to find: " + 'Provides the `AuthProvider` component and `useAuth` hook that gate access to the UI when the server requires authentication. Handles credential storage, validation, and session invalidation.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/auth/AGENTS.md')
    assert 'Does NOT implement the login form UI — that lives in `src/routes/`. Does NOT make authenticated API requests — it only validates credentials via `/admin/version`.' in text, "expected to find: " + 'Does NOT implement the login form UI — that lives in `src/routes/`. Does NOT make authenticated API requests — it only validates credentials via `/admin/version`.'[:80]

