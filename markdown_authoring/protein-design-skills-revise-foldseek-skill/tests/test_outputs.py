"""Behavioral checks for protein-design-skills-revise-foldseek-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/protein-design-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/foldseek/SKILL.md')
    assert '| `--max-seqs` | 300 | Max hits to pass through prefilter; reducing this affects sensitivity |' in text, "expected to find: " + '| `--max-seqs` | 300 | Max hits to pass through prefilter; reducing this affects sensitivity |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/foldseek/SKILL.md')
    assert '### Option 1: Web Server (Quick; rate-limited, use sparingly)' in text, "expected to find: " + '### Option 1: Web Server (Quick; rate-limited, use sparingly)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/foldseek/SKILL.md')
    assert '└─ Functional annotation → Cross-reference with UniProt' in text, "expected to find: " + '└─ Functional annotation → Cross-reference with UniProt'[:80]

