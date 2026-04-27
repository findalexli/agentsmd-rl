"""Behavioral checks for prefect-docs-document-loaderdeps-pattern-for (markdown_authoring task).

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
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert '`loaderDeps` controls which search params re-trigger the loader. When the loader re-runs, the route re-suspends and all local UI state resets (accordion sections collapse, dialogs close, etc.).' in text, "expected to find: " + '`loaderDeps` controls which search params re-trigger the loader. When the loader re-runs, the route re-suspends and all local UI state resets (accordion sections collapse, dialogs close, etc.).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert 'Only include params that affect *what data* the loader fetches. Exclude params that only control UI state (pagination, active tab, open accordion):' in text, "expected to find: " + 'Only include params that affect *what data* the loader fetches. Exclude params that only control UI state (pagination, active tab, open accordion):'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert 'Forgetting this causes every pagination click to re-run the loader, which collapses open accordions and other ephemeral UI state.' in text, "expected to find: " + 'Forgetting this causes every pagination click to re-run the loader, which collapses open accordions and other ephemeral UI state.'[:80]

