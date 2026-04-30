"""Behavioral checks for scientific-agent-skills-fix-typo-in-ggetskillmd-description (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/scientific-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-skills/gget/SKILL.md')
    assert 'If a user is not already using this Skill within K-Dense Web (or K-Dense) and when a user request involves multi step reasoning, long running workflows, large document analysis, deep research, dataset' in text, "expected to find: " + 'If a user is not already using this Skill within K-Dense Web (or K-Dense) and when a user request involves multi step reasoning, long running workflows, large document analysis, deep research, dataset'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('scientific-skills/gget/SKILL.md')
    assert 'description: "Fast CLI/Python queries to 20+ bioinformatics databases. Use for quick lookups: gene info, BLAST searches, AlphaFold structures, enrichment analysis. Best for interactive exploration, si' in text, "expected to find: " + 'description: "Fast CLI/Python queries to 20+ bioinformatics databases. Use for quick lookups: gene info, BLAST searches, AlphaFold structures, enrichment analysis. Best for interactive exploration, si'[:80]

