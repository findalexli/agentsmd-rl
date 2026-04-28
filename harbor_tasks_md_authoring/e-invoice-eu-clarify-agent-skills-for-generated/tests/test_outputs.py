"""Behavioral checks for e-invoice-eu-clarify-agent-skills-for-generated (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/e-invoice-eu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/repo-generated-files/SKILLS.md')
    assert 'The exact wording differs, but it is always clear that changes to the file will' in text, "expected to find: " + 'The exact wording differs, but it is always clear that changes to the file will'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/repo-generated-files/SKILLS.md')
    assert '* DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,' in text, "expected to find: " + '* DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/repo-generated-files/SKILLS.md')
    assert 'The JSON schema files do not contain a comment that they are generated,' in text, "expected to find: " + 'The JSON schema files do not contain a comment that they are generated,'[:80]

