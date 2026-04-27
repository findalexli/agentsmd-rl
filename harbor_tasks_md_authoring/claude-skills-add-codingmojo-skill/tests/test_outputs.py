"""Behavioral checks for claude-skills-add-codingmojo-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('coding-mojo/SKILL.md')
    assert 'description: Develop and run Mojo code in Claude.ai containers. Handles installation, compilation, and execution. Use when writing Mojo code, benchmarking Mojo vs Python, or when user mentions Mojo, M' in text, "expected to find: " + 'description: Develop and run Mojo code in Claude.ai containers. Handles installation, compilation, and execution. Use when writing Mojo code, benchmarking Mojo vs Python, or when user mentions Mojo, M'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('coding-mojo/SKILL.md')
    assert 'Mojo is a systems programming language from Modular that combines Python-like syntax with C-level performance. This skill handles container setup and execution. For **language syntax and semantics**, ' in text, "expected to find: " + 'Mojo is a systems programming language from Modular that combines Python-like syntax with C-level performance. This skill handles container setup and execution. For **language syntax and semantics**, '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('coding-mojo/SKILL.md')
    assert 'Expected: Mojo is 50-100x faster than CPython on tight numeric loops. SIMD and parallelism widen the gap further but require mojo-syntax and mojo-gpu-fundamentals skills for correct usage.' in text, "expected to find: " + 'Expected: Mojo is 50-100x faster than CPython on tight numeric loops. SIMD and parallelism widen the gap further but require mojo-syntax and mojo-gpu-fundamentals skills for correct usage.'[:80]

