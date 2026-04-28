"""Behavioral checks for monorepo-agents-add-custom-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/monorepo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '../AGENTS.md' in text, "expected to find: " + '../AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When reviewing PRs, focus the majority of your effort on correctness and performance (not style). Pay special attention to bugs' in text, "expected to find: " + 'When reviewing PRs, focus the majority of your effort on correctness and performance (not style). Pay special attention to bugs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'that can be caused by malicious participants when a function accepts untrusted input. This repository is designed to be' in text, "expected to find: " + 'that can be caused by malicious participants when a function accepts untrusted input. This repository is designed to be'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'used in adversarial environments, and as such, we should be extra careful to ensure that the code is robust.' in text, "expected to find: " + 'used in adversarial environments, and as such, we should be extra careful to ensure that the code is robust.'[:80]

