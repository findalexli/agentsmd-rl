"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-comprehensive-me (markdown_authoring task).

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
    text = _read('skills/mermaid-diagram/SKILL.md')
    assert 'Mermaid supports rendering mathematical expressions via KaTeX (v10.9.0+). **When the diagram content involves math** (formulas, equations, Greek letters, subscripts/superscripts, fractions, matrices, ' in text, "expected to find: " + 'Mermaid supports rendering mathematical expressions via KaTeX (v10.9.0+). **When the diagram content involves math** (formulas, equations, Greek letters, subscripts/superscripts, fractions, matrices, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mermaid-diagram/SKILL.md')
    assert 'Think of the diagram as an invisible grid. Use `junction` nodes as virtual anchor points on that grid to precisely control where each component is placed. This is especially useful when a direct edge ' in text, "expected to find: " + 'Think of the diagram as an invisible grid. Use `junction` nodes as virtual anchor points on that grid to precisely control where each component is placed. This is especially useful when a direct edge '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mermaid-diagram/SKILL.md')
    assert 'description: Generate Mermaid diagrams from user requirements. Saves .mmd and .md files to figures/ directory with syntax verification. Supports flowcharts, sequence diagrams, class diagrams, ER diagr' in text, "expected to find: " + 'description: Generate Mermaid diagrams from user requirements. Saves .mmd and .md files to figures/ directory with syntax verification. Supports flowcharts, sequence diagrams, class diagrams, ER diagr'[:80]

