"""Behavioral checks for train-chef26076-create-comprehensive-github-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/train")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Remember: All tasks should be prompt-based with explicit confirmation at each step, maintaining high code quality and test coverage standards throughout the process. Consider Train's transport archite" in text, "expected to find: " + "Remember: All tasks should be prompt-based with explicit confirmation at each step, maintaining high code quality and test coverage standards throughout the process. Consider Train's transport archite"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains the Train Transport Interface, a Ruby library that provides a unified interface to talk to local or remote operating systems and APIs. Train is a core component of the Chef In' in text, "expected to find: " + 'This repository contains the Train Transport Interface, a Ruby library that provides a unified interface to talk to local or remote operating systems and APIs. Train is a core component of the Chef In'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '✅ Create PR with ai-assisted label (if label doesn\'t exist, create it with description "Work completed with AI assistance following Progress AI policies" and color "9A4DFF")' in text, "expected to find: " + '✅ Create PR with ai-assisted label (if label doesn\'t exist, create it with description "Work completed with AI assistance following Progress AI policies" and color "9A4DFF")'[:80]

