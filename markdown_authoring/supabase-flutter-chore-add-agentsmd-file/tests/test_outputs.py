"""Behavioral checks for supabase-flutter-chore-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/supabase-flutter")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a monorepo for the Supabase Flutter SDK, managed by [Melos](https://melos.invertase.dev/). It contains multiple independently versioned packages that provide Flutter and Dart clients for Supab' in text, "expected to find: " + 'This is a monorepo for the Supabase Flutter SDK, managed by [Melos](https://melos.invertase.dev/). It contains multiple independently versioned packages that provide Flutter and Dart clients for Supab'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `-j 1` flag runs tests sequentially (not concurrently), which is required since tests share the same Docker services.' in text, "expected to find: " + 'The `-j 1` flag runs tests sequentially (not concurrently), which is required since tests share the same Docker services.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **gotrue**: `AuthException` (base), with specialized subclasses like `AuthApiException`, `AuthRetryableFetchException`' in text, "expected to find: " + '- **gotrue**: `AuthException` (base), with specialized subclasses like `AuthApiException`, `AuthRetryableFetchException`'[:80]

