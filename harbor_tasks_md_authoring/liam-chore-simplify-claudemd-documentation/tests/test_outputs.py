"""Behavioral checks for liam-chore-simplify-claudemd-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/liam")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious' in text, "expected to find: " + '- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For database migration and type generation workflows, see @docs/migrationOpsContext.md.' in text, "expected to find: " + 'For database migration and type generation workflows, see @docs/migrationOpsContext.md.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- [`docs/langgraph/README.md`](docs/langgraph/README.md) - LangGraph.js complete guide' in text, "expected to find: " + '- [`docs/langgraph/README.md`](docs/langgraph/README.md) - LangGraph.js complete guide'[:80]

