"""Behavioral checks for prd-taskmaster-feat-use-templates-for-prd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prd-taskmaster")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "**IMPORTANT**: Generate a TDD workflow guide for the project using the template, but only if one doesn't already exist." in text, "expected to find: " + "**IMPORTANT**: Generate a TDD workflow guide for the project using the template, but only if one doesn't already exist."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- Complex/Standard projects: Use Read tool to load templates/taskmaster-prd-comprehensive.md' in text, "expected to find: " + '- Complex/Standard projects: Use Read tool to load templates/taskmaster-prd-comprehensive.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '{{TECH_STACK}}          → Tech stack from discovery (e.g., "React, Node.js, PostgreSQL")' in text, "expected to find: " + '{{TECH_STACK}}          → Tech stack from discovery (e.g., "React, Node.js, PostgreSQL")'[:80]

