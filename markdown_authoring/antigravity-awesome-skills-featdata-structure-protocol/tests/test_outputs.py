"""Behavioral checks for antigravity-awesome-skills-featdata-structure-protocol (markdown_authoring task).

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
    text = _read('skills/data-structure-protocol/SKILL.md')
    assert 'DSP is NOT documentation for humans and NOT an AST dump. It captures three things: **meaning** (why an entity exists), **boundaries** (what it imports and exposes), and **reasons** (why each connectio' in text, "expected to find: " + 'DSP is NOT documentation for humans and NOT an AST dump. It captures three things: **meaning** (why an entity exists), **boundaries** (what it imports and exposes), and **reasons** (why each connectio'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-structure-protocol/SKILL.md')
    assert 'LLM coding agents lose context between tasks. On large codebases they spend most of their tokens on "orientation" — figuring out where things live, what depends on what, and what is safe to change. DS' in text, "expected to find: " + 'LLM coding agents lose context between tasks. On large codebases they spend most of their tokens on "orientation" — figuring out where things live, what depends on what, and what is safe to change. DS'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data-structure-protocol/SKILL.md')
    assert 'When an import is recorded, DSP stores a short reason explaining *why* that dependency exists. This lives in the `exports/` reverse index of the imported entity. A dependency graph without reasons tel' in text, "expected to find: " + 'When an import is recorded, DSP stores a short reason explaining *why* that dependency exists. This lives in the `exports/` reverse index of the imported entity. A dependency graph without reasons tel'[:80]

