"""Behavioral checks for prefect-update-agentsmd-files-for-c1c14fe (markdown_authoring task).

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
    text = _read('docs/AGENTS.md')
    assert '1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/`, and `integrations/<name>/api-ref/` are generated from source code.' in text, "expected to find: " + '1. **Do not edit auto-generated files.** Pages under `v3/examples/`, `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/`, and `integrations/<name>/api-ref/` are generated from source code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/` — generated API reference (Python SDK, CLI, REST API)' in text, "expected to find: " + '- `v3/api-ref/python/`, `v3/api-ref/cli/`, `v3/api-ref/rest-api/` — generated API reference (Python SDK, CLI, REST API)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert '- `v3/api-ref/events/` is **hand-authored** and should be edited directly when event schemas change' in text, "expected to find: " + '- `v3/api-ref/events/` is **hand-authored** and should be edited directly when event schemas change'[:80]

