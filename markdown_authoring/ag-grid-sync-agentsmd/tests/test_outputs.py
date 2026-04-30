"""Behavioral checks for ag-grid-sync-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ag-grid")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'While this transition is in progress, changes made to Theming API should be applied to Legacy Themes. When reviewing a PR with changes to the Theming API CSS, if the same PR does not have correspondin' in text, "expected to find: " + 'While this transition is in progress, changes made to Theming API should be applied to Legacy Themes. When reviewing a PR with changes to the Theming API CSS, if the same PR does not have correspondin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The grid is in transition from Legacy Themes (.scss files written in Sass under `/community-modules/styles/`) to the Theming API (.css written in modern nested CSS under `/packages/`).' in text, "expected to find: " + 'The grid is in transition from Legacy Themes (.scss files written in Sass under `/community-modules/styles/`) to the Theming API (.css written in modern nested CSS under `/packages/`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '#### Styling' in text, "expected to find: " + '#### Styling'[:80]

