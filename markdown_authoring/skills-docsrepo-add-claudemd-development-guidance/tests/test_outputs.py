"""Behavioral checks for skills-docsrepo-add-claudemd-development-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'A collection of Claude Skills published by Posit PBC. Skills are structured markdown files that teach Claude specialized workflows (e.g., Shiny app development, R package testing, GitHub PR workflows)' in text, "expected to find: " + 'A collection of Claude Skills published by Posit PBC. Skills are structured markdown files that teach Claude specialized workflows (e.g., Shiny app development, R package testing, GitHub PR workflows)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Progressive disclosure**: Put specialized or large reference content in `references/*.md` and instruct Claude to read those files only when needed. This keeps the main `SKILL.md` within token limi' in text, "expected to find: " + '- **Progressive disclosure**: Put specialized or large reference content in `references/*.md` and instruct Claude to read those files only when needed. This keeps the main `SKILL.md` within token limi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'If a skill spans multiple categories (like `brand-yml` for both Shiny and Quarto), add its path to multiple plugin `skills` arrays. The `source` field is always `"./"` (repo root).' in text, "expected to find: " + 'If a skill spans multiple categories (like `brand-yml` for both Shiny and Quarto), add its path to multiple plugin `skills` arrays. The `source` field is always `"./"` (repo root).'[:80]

