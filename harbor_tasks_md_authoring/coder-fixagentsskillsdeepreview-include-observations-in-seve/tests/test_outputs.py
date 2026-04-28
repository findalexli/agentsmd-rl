"""Behavioral checks for coder-fixagentsskillsdeepreview-include-observations-in-seve (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/coder")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deep-review/SKILL.md')
    assert '- **Unnecessary novelty.** New files, new naming patterns, new abstractions where the existing codebase already has a convention. If no reviewer flagged it but you see it, add it. If a reviewer flagge' in text, "expected to find: " + '- **Unnecessary novelty.** New files, new naming patterns, new abstractions where the existing codebase already has a convention. If no reviewer flagged it but you see it, add it. If a reviewer flagge'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deep-review/SKILL.md')
    assert 'For each finding **and observation**, apply the severity test in **both directions**. Observations are not exempt — a reviewer may underrate a convention violation or a missing guarantee as Obs when t' in text, "expected to find: " + 'For each finding **and observation**, apply the severity test in **both directions**. Observations are not exempt — a reviewer may underrate a convention violation or a missing guarantee as Obs when t'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/deep-review/SKILL.md')
    assert '"body": "Summary of what\'s good and what to look at.\\n1 P2, 1 P3 across 2 inline comments.",' in text, "expected to find: " + '"body": "Summary of what\'s good and what to look at.\\n1 P2, 1 P3 across 2 inline comments.",'[:80]

