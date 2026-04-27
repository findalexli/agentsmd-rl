"""Behavioral checks for claude-code-sub-agents-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-sub-agents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'E -- YES ---> F[Use subset of previous team<br/>Max 3 agents]' in text, "expected to find: " + 'E -- YES ---> F[Use subset of previous team<br/>Max 3 agents]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'G -- YES --> H[Handle directly without sub-agents]' in text, "expected to find: " + 'G -- YES --> H[Handle directly without sub-agents]'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'C -- NO --> D[**Invoke agent_organizer**];' in text, "expected to find: " + 'C -- NO --> D[**Invoke agent_organizer**];'[:80]

