"""Behavioral checks for prefect-update-agentsmd-files-for-96c99bc (markdown_authoring task).

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
    text = _read('tests/AGENTS.md')
    assert '- **Retrying HTTP requests** (`hosted_api_client` tests): SQLite "database is locked" 503 errors can occur due to concurrent access. Retry the HTTP request inside the loop; keep the result assertions ' in text, "expected to find: " + '- **Retrying HTTP requests** (`hosted_api_client` tests): SQLite "database is locked" 503 errors can occur due to concurrent access. Retry the HTTP request inside the loop; keep the result assertions '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert '- **Retrying assertions for async event propagation** (most common): wrap the assertion inside `with attempt:` so it retries until the event arrives.' in text, "expected to find: " + '- **Retrying assertions for async event propagation** (most common): wrap the assertion inside `with attempt:` so it retries until the event arrives.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/AGENTS.md')
    assert 'Use `retry_asserts` from `prefect._internal.testing` to handle timing-sensitive assertions. Two patterns:' in text, "expected to find: " + 'Use `retry_asserts` from `prefect._internal.testing` to handle timing-sensitive assertions. Two patterns:'[:80]

