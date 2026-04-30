"""Behavioral checks for jira-skill-fix-align-skillmd-description-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jira-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-communication/SKILL.md')
    assert 'description: "Use when interacting with Jira issues - searching, creating, updating, transitioning, commenting, logging work, downloading attachments, managing sprints, boards, issue links, fields, or' in text, "expected to find: " + 'description: "Use when interacting with Jira issues - searching, creating, updating, transitioning, commenting, logging work, downloading attachments, managing sprints, boards, issue links, fields, or'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/jira-syntax/SKILL.md')
    assert 'description: "Use when writing Jira descriptions or comments, converting Markdown to Jira wiki markup, using templates (bug reports, feature requests), or validating Jira syntax before submission."' in text, "expected to find: " + 'description: "Use when writing Jira descriptions or comments, converting Markdown to Jira wiki markup, using templates (bug reports, feature requests), or validating Jira syntax before submission."'[:80]

