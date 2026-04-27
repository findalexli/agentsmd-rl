"""Behavioral checks for openjudge-featbib-verify-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openjudge")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bib-verify/SKILL.md')
    assert '- Combined PDF review + BibTeX verification: [../paper-review/SKILL.md](../paper-review/SKILL.md)' in text, "expected to find: " + '- Combined PDF review + BibTeX verification: [../paper-review/SKILL.md](../paper-review/SKILL.md)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bib-verify/SKILL.md')
    assert '| `suspect` | Title or authors do not match any real paper — likely hallucinated or mis-cited |' in text, "expected to find: " + '| `suspect` | Title or authors do not match any real paper — likely hallucinated or mis-cited |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bib-verify/SKILL.md')
    assert '- Full pipeline options: [../paper-review/reference.md](../paper-review/reference.md)' in text, "expected to find: " + '- Full pipeline options: [../paper-review/reference.md](../paper-review/reference.md)'[:80]

