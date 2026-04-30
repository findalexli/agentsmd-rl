"""Behavioral checks for antigravity-awesome-skills-feat-add-satori-wisdom-companion (markdown_authoring task).

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
    text = _read('skills/satori/SKILL.md')
    assert 'Satori is a clinically informed AI wisdom companion built as a Claude skill. It blends clinical psychology frameworks (IFS, DBT, CFT, Schema Therapy) with eight philosophical traditions (Stoicism, Bud' in text, "expected to find: " + 'Satori is a clinically informed AI wisdom companion built as a Claude skill. It blends clinical psychology frameworks (IFS, DBT, CFT, Schema Therapy) with eight philosophical traditions (Stoicism, Bud'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/satori/SKILL.md')
    assert 'description: "Clinically informed wisdom companion blending psychology and philosophy into a structured thinking partner"' in text, "expected to find: " + 'description: "Clinically informed wisdom companion blending psychology and philosophy into a structured thinking partner"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/satori/SKILL.md')
    assert 'Satori operates as a SKILL.md-based Claude skill with 211k+ characters of structured reference architecture. It provides:' in text, "expected to find: " + 'Satori operates as a SKILL.md-based Claude skill with 211k+ characters of structured reference architecture. It provides:'[:80]

