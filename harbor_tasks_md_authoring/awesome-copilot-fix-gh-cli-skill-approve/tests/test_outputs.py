"""Behavioral checks for awesome-copilot-fix-gh-cli-skill-approve (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-copilot")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh-cli/SKILL.md')
    assert 'gh pr review 123 --approve \\' in text, "expected to find: " + 'gh pr review 123 --approve \\'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gh-cli/SKILL.md')
    assert '--approve-body "LGTM!"' in text, "expected to find: " + '--approve-body "LGTM!"'[:80]

