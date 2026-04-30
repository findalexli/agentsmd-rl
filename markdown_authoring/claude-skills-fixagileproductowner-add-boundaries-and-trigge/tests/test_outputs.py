"""Behavioral checks for claude-skills-fixagileproductowner-add-boundaries-and-trigge (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('product-team/agile-product-owner/SKILL.md')
    assert 'not_for: Kanban-only workflows, waterfall project planning, general task management, non-Scrum agile frameworks (SAFe, LeSS) without adaptation' in text, "expected to find: " + 'not_for: Kanban-only workflows, waterfall project planning, general task management, non-Scrum agile frameworks (SAFe, LeSS) without adaptation'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('product-team/agile-product-owner/SKILL.md')
    assert "- **Acceptance criteria scaled by story size:** minimum AC counts map to story points to avoid under-spec'ing large items." in text, "expected to find: " + "- **Acceptance criteria scaled by story size:** minimum AC counts map to story points to avoid under-spec'ing large items."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('product-team/agile-product-owner/SKILL.md')
    assert '- **Weighted prioritization that stays consistent:** value 40%, impact 30%, risk 15%, effort 15% keeps tradeoffs explicit.' in text, "expected to find: " + '- **Weighted prioritization that stays consistent:** value 40%, impact 30%, risk 15%, effort 15% keeps tradeoffs explicit.'[:80]

