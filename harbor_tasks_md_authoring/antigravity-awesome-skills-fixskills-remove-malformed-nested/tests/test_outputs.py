"""Behavioral checks for antigravity-awesome-skills-fixskills-remove-malformed-nested (markdown_authoring task).

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
    text = _read('skills/browser-extension-builder/SKILL.md')
    assert 'skills/browser-extension-builder/SKILL.md' in text, "expected to find: " + 'skills/browser-extension-builder/SKILL.md'[:80]

