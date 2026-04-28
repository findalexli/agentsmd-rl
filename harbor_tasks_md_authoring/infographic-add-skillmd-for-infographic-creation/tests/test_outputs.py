"""Behavioral checks for infographic-add-skillmd-for-infographic-creation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/infographic")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'AntV Infographic Syntax is a mermaid-like DSL for describing infographic rendering configuration. It uses indentation to describe information, has strong robustness, and makes it easy to render infogr' in text, "expected to find: " + 'AntV Infographic Syntax is a mermaid-like DSL for describing infographic rendering configuration. It uses indentation to describe information, has strong robustness, and makes it easy to render infogr'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'An infographic (Infographic) transforms data, information, and knowledge into perceivable visual language. It combines visual design with data visualization, using intuitive symbols to compress comple' in text, "expected to find: " + 'An infographic (Infographic) transforms data, information, and knowledge into perceivable visual language. It combines visual design with data visualization, using intuitive symbols to compress comple'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "Before creating the infographic, it is important to understand the user's requirements and the information they want to present. This will help in defining the template and the data structure." in text, "expected to find: " + "Before creating the infographic, it is important to understand the user's requirements and the information they want to present. This will help in defining the template and the data structure."[:80]

