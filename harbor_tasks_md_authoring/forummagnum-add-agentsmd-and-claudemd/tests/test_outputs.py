"""Behavioral checks for forummagnum-add-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/forummagnum")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Some server SQL logic is generated from fragment definitions, so fragments are' in text, "expected to find: " + '- Some server SQL logic is generated from fragment definitions, so fragments are'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Many old file and symbol names still say LessWrong even when the code is used' in text, "expected to find: " + '- Many old file and symbol names still say LessWrong even when the code is used'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- A lot of business logic runs in collection callbacks around mutations, not in' in text, "expected to find: " + '- A lot of business logic runs in collection callbacks around mutations, not in'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See [AGENTS.md](AGENTS.md).' in text, "expected to find: " + 'See [AGENTS.md](AGENTS.md).'[:80]

