"""Behavioral checks for slack-gamebot-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/slack-gamebot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "git branch --merged master | grep -v '^\\* \\|^  master$' | xargs -r git branch -d" in text, "expected to find: " + "git branch --merged master | grep -v '^\\* \\|^  master$' | xargs -r git branch -d"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Never push directly to master — always work on a branch and open a PR.' in text, "expected to find: " + '- Never push directly to master — always work on a branch and open a PR.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Before creating a new branch, always sync and clean up:' in text, "expected to find: " + 'Before creating a new branch, always sync and clean up:'[:80]

