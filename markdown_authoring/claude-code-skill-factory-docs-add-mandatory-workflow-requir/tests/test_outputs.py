"""Behavioral checks for claude-code-skill-factory-docs-add-mandatory-workflow-requir (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-skill-factory")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- ✅ **Automation leverage**: Uses the excellent GitHub automation built into this repo' in text, "expected to find: " + '- ✅ **Automation leverage**: Uses the excellent GitHub automation built into this repo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CRITICAL**: All work on this project MUST follow this workflow. **NO EXCEPTIONS.**' in text, "expected to find: " + '**CRITICAL**: All work on this project MUST follow this workflow. **NO EXCEPTIONS.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- ✅ **Proper tracking**: Every task is tracked in GitHub issues and project board' in text, "expected to find: " + '- ✅ **Proper tracking**: Every task is tracked in GitHub issues and project board'[:80]

