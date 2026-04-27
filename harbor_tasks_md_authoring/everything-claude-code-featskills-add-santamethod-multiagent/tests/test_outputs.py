"""Behavioral checks for everything-claude-code-featskills-add-santamethod-multiagent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/santa-method/SKILL.md')
    assert 'The core insight: a single agent reviewing its own output shares the same biases, knowledge gaps, and systematic errors that produced the output. Two independent reviewers with no shared context break' in text, "expected to find: " + 'The core insight: a single agent reviewing its own output shares the same biases, knowledge gaps, and systematic errors that produced the output. Two independent reviewers with no shared context break'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/santa-method/SKILL.md')
    assert "Why both must pass: if only one reviewer catches an issue, that issue is real. The other reviewer's blind spot is exactly the failure mode Santa Method exists to eliminate." in text, "expected to find: " + "Why both must pass: if only one reviewer catches an issue, that issue is real. The other reviewer's blind spot is exactly the failure mode Santa Method exists to eliminate."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/santa-method/SKILL.md')
    assert '| Reviewer agreement bias | Both reviewers miss the same thing | Mitigated by independence, not eliminated. For critical output, add a third reviewer or human spot-check. |' in text, "expected to find: " + '| Reviewer agreement bias | Both reviewers miss the same thing | Mitigated by independence, not eliminated. For critical output, add a third reviewer or human spot-check. |'[:80]

