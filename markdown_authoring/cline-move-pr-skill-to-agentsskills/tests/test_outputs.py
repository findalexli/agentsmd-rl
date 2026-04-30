"""Behavioral checks for cline-move-pr-skill-to-agentsskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-pull-request/SKILL.md')
    assert 'description: Create a GitHub pull request following project conventions. Use when the user asks to create a PR, submit changes for review, or open a pull request. Handles commit analysis, branch manag' in text, "expected to find: " + 'description: Create a GitHub pull request following project conventions. Use when the user asks to create a PR, submit changes for review, or open a pull request. Handles commit analysis, branch manag'[:80]

