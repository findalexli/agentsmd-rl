"""Behavioral checks for agent-skills-skills-align-elegantreports-skill-contract (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/elegant-reports/SKILL.md')
    assert '- Do not send sensitive source documents to third-party services unless the user explicitly requested PDF generation through Nutrient DWS and accepts that network boundary.' in text, "expected to find: " + '- Do not send sensitive source documents to third-party services unless the user explicitly requested PDF generation through Nutrient DWS and accepts that network boundary.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/elegant-reports/SKILL.md')
    assert '- file_read: "Reads bundled templates, themes, examples, and design references inside the skill directory plus user-approved input markdown files."' in text, "expected to find: " + '- file_read: "Reads bundled templates, themes, examples, and design references inside the skill directory plus user-approved input markdown files."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/elegant-reports/SKILL.md')
    assert '- Do not install extra packages, change dependency versions, or add new external services unless the user explicitly asks for that setup work.' in text, "expected to find: " + '- Do not install extra packages, change dependency versions, or add new external services unless the user explicitly asks for that setup work.'[:80]

