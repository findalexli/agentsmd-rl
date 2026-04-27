"""Behavioral checks for planning-with-files-feat-improve-skill-metadata-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/planning-with-files")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'description: Implements Manus-style file-based planning to organize and track progress on complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when asked to plan out, break down, or ' in text, "expected to find: " + 'description: Implements Manus-style file-based planning to organize and track progress on complex tasks. Creates task_plan.md, findings.md, and progress.md. Use when asked to plan out, break down, or '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch"' in text, "expected to find: " + 'allowed-tools: "Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/planning-with-files/SKILL.md')
    assert 'version: "2.10.0"' in text, "expected to find: " + 'version: "2.10.0"'[:80]

