"""Behavioral checks for antigravity-awesome-skills-fixpromptengineer-add-missing-ste (markdown_authoring task).

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
    text = _read('skills/prompt-engineer/SKILL.md')
    assert '**Critical Rule:** When in doubt, skip clarification and generate the best prompt with available context. Over-asking breaks the "magic mode" experience.' in text, "expected to find: " + '**Critical Rule:** When in doubt, skip clarification and generate the best prompt with available context. Over-asking breaks the "magic mode" experience.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prompt-engineer/SKILL.md')
    assert '**Objective:** Gather missing information only when it is critical to framework selection or prompt quality.' in text, "expected to find: " + '**Objective:** Gather missing information only when it is critical to framework selection or prompt quality.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/prompt-engineer/SKILL.md')
    assert '1. What do you want to do with AI — build something, learn about it, or use an AI tool for a task?"' in text, "expected to find: " + '1. What do you want to do with AI — build something, learn about it, or use an AI tool for a task?"'[:80]

