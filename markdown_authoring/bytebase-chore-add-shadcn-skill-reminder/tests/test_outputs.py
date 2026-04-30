"""Behavioral checks for bytebase-chore-add-shadcn-skill-reminder (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bytebase")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert 'When working on React UI, invoke the `shadcn` skill before writing or modifying components. The skill provides component selection guidance, critical rules, and best practices. Always check the skill ' in text, "expected to find: " + 'When working on React UI, invoke the `shadcn` skill before writing or modifying components. The skill provides component selection guidance, critical rules, and best practices. Always check the skill '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert '## shadcn Skill' in text, "expected to find: " + '## shadcn Skill'[:80]

