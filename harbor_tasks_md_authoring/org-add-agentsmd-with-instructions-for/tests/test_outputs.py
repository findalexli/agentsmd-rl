"""Behavioral checks for org-add-agentsmd-with-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/org")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- NEVER use keywords that automatically close issues: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`' in text, "expected to find: " + '- NEVER use keywords that automatically close issues: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use `make add-members WHO=username1,username2 REPOS=kubernetes-sigs,kubernetes` which automatically creates compliant commits' in text, "expected to find: " + '- Use `make add-members WHO=username1,username2 REPOS=kubernetes-sigs,kubernetes` which automatically creates compliant commits'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file contains specific instructions for AI agents and automated tools working in this repository.' in text, "expected to find: " + 'This file contains specific instructions for AI agents and automated tools working in this repository.'[:80]

