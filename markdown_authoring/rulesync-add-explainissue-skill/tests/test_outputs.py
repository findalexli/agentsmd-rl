"""Behavioral checks for rulesync-add-explainissue-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rulesync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/explain-issue/SKILL.md')
    assert '2. **Proposed Solution:** What solution, direction, or next step is suggested in the issue discussion? Summarize the expected approach, scope, and important constraints if they are mentioned.' in text, "expected to find: " + '2. **Proposed Solution:** What solution, direction, or next step is suggested in the issue discussion? Summarize the expected approach, scope, and important constraints if they are mentioned.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/explain-issue/SKILL.md')
    assert 'If the issue references related pull requests, commits, or files that are needed to understand the solution, gather that context as well.' in text, "expected to find: " + 'If the issue references related pull requests, commits, or files that are needed to understand the solution, gather that context as well.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/explain-issue/SKILL.md')
    assert 'If the issue does not contain enough information about the solution, explicitly say that the solution is still undecided or unspecified.' in text, "expected to find: " + 'If the issue does not contain enough information about the solution, explicitly say that the solution is still undecided or unspecified.'[:80]

