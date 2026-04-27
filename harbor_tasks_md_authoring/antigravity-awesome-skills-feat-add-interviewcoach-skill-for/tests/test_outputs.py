"""Behavioral checks for antigravity-awesome-skills-feat-add-interviewcoach-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview-coach/SKILL.md')
    assert 'description: "Full job search coaching system — JD decoding, resume, storybank, mock interviews, transcript analysis, comp negotiation. 23 commands, persistent state."' in text, "expected to find: " + 'description: "Full job search coaching system — JD decoding, resume, storybank, mock interviews, transcript analysis, comp negotiation. 23 commands, persistent state."'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview-coach/SKILL.md')
    assert '- **Storybank** — STAR stories with earned secrets, retrieval drills, portfolio optimization' in text, "expected to find: " + '- **Storybank** — STAR stories with earned secrets, retrieval drills, portfolio optimization'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview-coach/SKILL.md')
    assert '- **Comp + negotiation** — pre-offer scripting, offer analysis, exact negotiation scripts' in text, "expected to find: " + '- **Comp + negotiation** — pre-offer scripting, offer analysis, exact negotiation scripts'[:80]

