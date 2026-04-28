"""Behavioral checks for prefect-update-agentsmd-files-for-2793f36 (markdown_authoring task).

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
    text = _read('src/prefect/AGENTS.md')
    assert '- `testing/` → Test utilities shipped with the SDK: `prefect_test_harness`, assertion helpers, and reusable fixtures (see testing/AGENTS.md)' in text, "expected to find: " + '- `testing/` → Test utilities shipped with the SDK: `prefect_test_harness`, assertion helpers, and reusable fixtures (see testing/AGENTS.md)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/testing/AGENTS.md')
    assert '- **`prefect_test_harness` registers the test server under `SubprocessASGIServer._instances[None]`.** `SubprocessASGIServer` is a port-keyed singleton. The harness creates a server with an explicit po' in text, "expected to find: " + '- **`prefect_test_harness` registers the test server under `SubprocessASGIServer._instances[None]`.** `SubprocessASGIServer` is a port-keyed singleton. The harness creates a server with an explicit po'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/testing/AGENTS.md')
    assert '- **`prefect_test_harness()`** (`utilities.py`) — Context manager that spins up a temporary SQLite-backed `SubprocessASGIServer` and overrides `PREFECT_API_URL` for the duration of the block. Safe to ' in text, "expected to find: " + '- **`prefect_test_harness()`** (`utilities.py`) — Context manager that spins up a temporary SQLite-backed `SubprocessASGIServer` and overrides `PREFECT_API_URL` for the duration of the block. Safe to '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/testing/AGENTS.md')
    assert 'Provides the `prefect_test_harness` context manager and assertion helpers consumed by both the Prefect test suite and downstream user code. Does **not** own pytest fixtures (those live in `tests/`) or' in text, "expected to find: " + 'Provides the `prefect_test_harness` context manager and assertion helpers consumed by both the Prefect test suite and downstream user code. Does **not** own pytest fixtures (those live in `tests/`) or'[:80]

