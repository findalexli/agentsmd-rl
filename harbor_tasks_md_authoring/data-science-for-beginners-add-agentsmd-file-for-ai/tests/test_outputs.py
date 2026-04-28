"""Behavioral checks for data-science-for-beginners-add-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/data-science-for-beginners")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Data Science for Beginners is a comprehensive 10-week, 20-lesson curriculum created by Microsoft Azure Cloud Advocates. The repository is a learning resource that teaches foundational data science con' in text, "expected to find: " + 'Data Science for Beginners is a comprehensive 10-week, 20-lesson curriculum created by Microsoft Azure Cloud Advocates. The repository is a learning resource that teaches foundational data science con'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Discussion Forum: https://github.com/microsoft/Data-Science-For-Beginners/discussions' in text, "expected to find: " + '- Discussion Forum: https://github.com/microsoft/Data-Science-For-Beginners/discussions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Other Microsoft curricula: ML for Beginners, AI for Beginners, Web Dev for Beginners' in text, "expected to find: " + '- Other Microsoft curricula: ML for Beginners, AI for Beginners, Web Dev for Beginners'[:80]

