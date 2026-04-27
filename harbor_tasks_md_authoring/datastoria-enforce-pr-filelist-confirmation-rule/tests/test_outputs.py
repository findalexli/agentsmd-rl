"""Behavioral checks for datastoria-enforce-pr-filelist-confirmation-rule (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/datastoria")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The agent must receive explicit user approval after showing those file lists before running any `gh pr create` command.' in text, "expected to find: " + '- The agent must receive explicit user approval after showing those file lists before running any `gh pr create` command.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The agent must receive explicit user approval after showing those file lists before running any `git push` command.' in text, "expected to find: " + '- The agent must receive explicit user approval after showing those file lists before running any `git push` command.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Push is blocked until the agent shows `Changed files vs origin/master` for each branch being pushed.' in text, "expected to find: " + '- Push is blocked until the agent shows `Changed files vs origin/master` for each branch being pushed.'[:80]

