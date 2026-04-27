"""Behavioral checks for linkedin-mcp-server-featskills-add-triagereviews-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/linkedin-mcp-server")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert 'Fetch all review comments on the current PR, verify each finding against real code, fix valid issues, and push.' in text, "expected to find: " + 'Fetch all review comments on the current PR, verify each finding against real code, fix valid issues, and push.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert '3. Extract unique findings — deduplicate across Copilot, Greptile, and human reviewers. Group by file and line.' in text, "expected to find: " + '3. Extract unique findings — deduplicate across Copilot, Greptile, and human reviewers. Group by file and line.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/triage-reviews/SKILL.md')
    assert 'description: Fetch PR review comments, verify each against real code/docs, fix valid issues, commit and push' in text, "expected to find: " + 'description: Fetch PR review comments, verify each against real code/docs, fix valid issues, commit and push'[:80]

