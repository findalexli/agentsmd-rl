"""Behavioral checks for change-lenses-and-actions-add-missing-frontmatter-block-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/change-lenses-and-actions")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'description: Run a structured behavioral diagnosis using COM-B, the Behavior Change Wheel, and BCT Taxonomy v1. Activate when the user describes a stuck or problematic behavior, or uses phrases like "' in text, "expected to find: " + 'description: Run a structured behavioral diagnosis using COM-B, the Behavior Change Wheel, and BCT Taxonomy v1. Activate when the user describes a stuck or problematic behavior, or uses phrases like "'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'name: com-b-diagnostic' in text, "expected to find: " + 'name: com-b-diagnostic'[:80]

