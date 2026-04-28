"""Behavioral checks for dstack-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Frontend: from `frontend/` run `npm install`, `npm run build`, then copy `frontend/build` into `src/dstack/_internal/server/statics/`; for dev, `npm run start` with API on port 8000.' in text, "expected to find: " + '- Frontend: from `frontend/` run `npm install`, `npm run build`, then copy `frontend/build` into `src/dstack/_internal/server/statics/`; for dev, `npm run start` with API on port 8000.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Core Python package lives in `src/dstack`; internal modules (including server) sit under `_internal`, API surfaces under `api`, and plugin integrations under `plugins`.' in text, "expected to find: " + '- Core Python package lives in `src/dstack`; internal modules (including server) sit under `_internal`, API surfaces under `api`, and plugin integrations under `plugins`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Commit messages follow the existing style: short, imperative summaries (e.g., “Fix exclude_not_available ignored”); include rationale in the body if needed.' in text, "expected to find: " + '- Commit messages follow the existing style: short, imperative summaries (e.g., “Fix exclude_not_available ignored”); include rationale in the body if needed.'[:80]

