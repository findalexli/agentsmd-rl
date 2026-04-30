"""Behavioral checks for antigravity-awesome-skills-feat-add-latexpaperconversion-ski (markdown_authoring task).

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
    text = _read('skills/latex-paper-conversion/SKILL.md')
    assert "This skill automates the tedious and recurring process of converting an academic paper written in LaTeX from one publisher's template to another. Different journals (e.g., Springer, MDPI, IEEE) have v" in text, "expected to find: " + "This skill automates the tedious and recurring process of converting an academic paper written in LaTeX from one publisher's template to another. Different journals (e.g., Springer, MDPI, IEEE) have v"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/latex-paper-conversion/SKILL.md')
    assert "Create a Python script (e.g., `convert_format.py`) to parse the source LaTeX file. Use Regular Expressions to extract core text blocks. Merge the new template's `preamble`, the extracted `body`, and t" in text, "expected to find: " + "Create a Python script (e.g., `convert_format.py`) to parse the source LaTeX file. Use Regular Expressions to extract core text blocks. Merge the new template's `preamble`, the extracted `body`, and t"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/latex-paper-conversion/SKILL.md')
    assert 'description: "This skill should be used when the user asks to convert an academic paper in LaTeX from one format (e.g., Springer, IPOL) to another format (e.g., MDPI, IEEE, Nature). It automates extra' in text, "expected to find: " + 'description: "This skill should be used when the user asks to convert an academic paper in LaTeX from one format (e.g., Springer, IPOL) to another format (e.g., MDPI, IEEE, Nature). It automates extra'[:80]

