"""Behavioral checks for gsd-2-fixskills-quote-skillmd-description-values (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gsd-2")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/resources/skills/verify-before-complete/SKILL.md')
    assert 'description: "Block completion claims until verification evidence has been produced in the current message. Use before marking a task/slice/milestone complete, before creating a commit or PR, before s' in text, "expected to find: " + 'description: "Block completion claims until verification evidence has been produced in the current message. Use before marking a task/slice/milestone complete, before creating a commit or PR, before s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/resources/skills/write-docs/SKILL.md')
    assert 'description: "Collaborative document authoring workflow for proposals, technical specs, decision docs, README sections, ADRs, and long-form prose that must work for fresh readers. Use when asked to \\"' in text, "expected to find: " + 'description: "Collaborative document authoring workflow for proposals, technical specs, decision docs, README sections, ADRs, and long-form prose that must work for fresh readers. Use when asked to \\"'[:80]

