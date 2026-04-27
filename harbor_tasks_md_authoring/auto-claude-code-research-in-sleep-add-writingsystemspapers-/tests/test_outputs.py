"""Behavioral checks for auto-claude-code-research-in-sleep-add-writingsystemspapers- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-systems-papers/SKILL.md')
    assert 'description: "Paragraph-level structural blueprint for 10-12 page systems papers targeting OSDI, SOSP, ASPLOS, NSDI, and EuroSys. Provides page allocation, paragraph templates, and writing patterns. U' in text, "expected to find: " + 'description: "Paragraph-level structural blueprint for 10-12 page systems papers targeting OSDI, SOSP, ASPLOS, NSDI, and EuroSys. Provides page allocation, paragraph templates, and writing patterns. U'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-systems-papers/SKILL.md')
    assert '**Boundary**: paper-write handles the generation workflow (LaTeX output, DBLP verification, section-by-section drafting). This skill provides the **structural skeleton** — page budgets, paragraph role' in text, "expected to find: " + '**Boundary**: paper-write handles the generation workflow (LaTeX output, DBLP verification, section-by-section drafting). This skill provides the **structural skeleton** — page budgets, paragraph role'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/writing-systems-papers/SKILL.md')
    assert '- **paper-write**: General paper generation workflow with citation verification. This skill complements it with systems-specific structural blueprints.' in text, "expected to find: " + '- **paper-write**: General paper generation workflow with citation verification. This skill complements it with systems-specific structural blueprints.'[:80]

