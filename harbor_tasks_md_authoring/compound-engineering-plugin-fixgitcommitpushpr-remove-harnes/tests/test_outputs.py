"""Behavioral checks for compound-engineering-plugin-fixgitcommitpushpr-remove-harnes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M,_Extended_Thinking)-D97757?logo=claude&logoColor=white)' in text, "expected to find: " + '![Claude Code](https://img.shields.io/badge/Opus_4.6_(1M,_Extended_Thinking)-D97757?logo=claude&logoColor=white)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'Fill in at PR creation time using the harness lookup (for logo and color) and model slug below.' in text, "expected to find: " + 'Fill in at PR creation time using the harness lookup (for logo and color) and model slug below.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '![HARNESS](https://img.shields.io/badge/MODEL_SLUG-COLOR?logo=LOGO&logoColor=white)' in text, "expected to find: " + '![HARNESS](https://img.shields.io/badge/MODEL_SLUG-COLOR?logo=LOGO&logoColor=white)'[:80]

