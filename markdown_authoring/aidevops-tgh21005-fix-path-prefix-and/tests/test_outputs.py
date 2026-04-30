"""Behavioral checks for aidevops-tgh21005-fix-path-prefix-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aidevops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert 'Hard rules: see "Framework Rules > Git Workflow > Pre-edit rules" below. Details: `.agents/workflows/pre-edit.md`.' in text, "expected to find: " + 'Hard rules: see "Framework Rules > Git Workflow > Pre-edit rules" below. Details: `.agents/workflows/pre-edit.md`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert 'Git is the audit trail. Procedures: see the "## Git Workflow" section below.' in text, "expected to find: " + 'Git is the audit trail. Procedures: see the "## Git Workflow" section below.'[:80]

