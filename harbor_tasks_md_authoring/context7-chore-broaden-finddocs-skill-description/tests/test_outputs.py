"""Behavioral checks for context7-chore-broaden-finddocs-skill-description (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/context7")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-docs/SKILL.md')
    assert 'Retrieves authoritative, up-to-date technical documentation, API references,' in text, "expected to find: " + 'Retrieves authoritative, up-to-date technical documentation, API references,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-docs/SKILL.md')
    assert 'programming languages, SDKs, APIs, CLI tools, cloud services, infrastructure' in text, "expected to find: " + 'programming languages, SDKs, APIs, CLI tools, cloud services, infrastructure'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/find-docs/SKILL.md')
    assert 'Use this skill whenever answering technical questions or writing code that' in text, "expected to find: " + 'Use this skill whenever answering technical questions or writing code that'[:80]

