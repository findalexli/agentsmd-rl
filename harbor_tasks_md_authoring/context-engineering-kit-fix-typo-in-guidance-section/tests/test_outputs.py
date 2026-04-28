"""Behavioral checks for context-engineering-kit-fix-typo-in-guidance-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/context-engineering-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/ddd/skills/software-architecture/SKILL.md')
    assert 'This skill provides guidance for quality focused software development and architecture. It is based on Clean Architecture and Domain Driven Design principles.' in text, "expected to find: " + 'This skill provides guidance for quality focused software development and architecture. It is based on Clean Architecture and Domain Driven Design principles.'[:80]

