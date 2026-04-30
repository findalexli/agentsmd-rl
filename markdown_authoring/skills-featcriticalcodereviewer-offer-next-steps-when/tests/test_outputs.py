"""Behavioral checks for skills-featcriticalcodereviewer-offer-next-steps-when (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert '- Submit your review verbatim as a PR comment with attribution at the top: "Review feedback assisted by the [critical-code-reviewer skill](https://github.com/posit-dev/skills/blob/main/posit-dev/criti' in text, "expected to find: " + '- Submit your review verbatim as a PR comment with attribution at the top: "Review feedback assisted by the [critical-code-reviewer skill](https://github.com/posit-dev/skills/blob/main/posit-dev/criti'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert 'NOTE: If you are operating as a subagent or as an agent for another coding assistant, e.g. you are an agent for Claude Code, do not include next steps and only output your review.' in text, "expected to find: " + 'NOTE: If you are operating as a subagent or as an agent for another coding assistant, e.g. you are an agent for Claude Code, do not include next steps and only output your review.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('posit-dev/critical-code-reviewer/SKILL.md')
    assert '- If the user chooses this option, use the AskUserQuestion tool to systematically talk through each of the issues identified in your review.' in text, "expected to find: " + '- If the user chooses this option, use the AskUserQuestion tool to systematically talk through each of the issues identified in your review.'[:80]

