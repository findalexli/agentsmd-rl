"""Behavioral checks for human-skill-tree-add-music-education-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/human-skill-tree")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/02-music-arts/SKILL.md')
    assert 'The goal is to guide learners through both the technical and expressive aspects of music. It helps users build strong foundations in rhythm, melody, harmony, and musical interpretation while encouragi' in text, "expected to find: " + 'The goal is to guide learners through both the technical and expressive aspects of music. It helps users build strong foundations in rhythm, melody, harmony, and musical interpretation while encouragi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/02-music-arts/SKILL.md')
    assert 'This skill teaches users how to learn and practice music effectively. It focuses on music theory fundamentals, instrument practice routines, ear training techniques, performance skills, and appreciati' in text, "expected to find: " + 'This skill teaches users how to learn and practice music effectively. It focuses on music theory fundamentals, instrument practice routines, ear training techniques, performance skills, and appreciati'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/02-music-arts/SKILL.md')
    assert 'In Western music, the most common scale is the major scale. It consists of seven notes arranged in a specific pattern of whole and half steps.' in text, "expected to find: " + 'In Western music, the most common scale is the major scale. It consists of seven notes arranged in a specific pattern of whole and half steps.'[:80]

