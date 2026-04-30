"""Behavioral checks for rhesis-docscursorrules-add-branch-creation-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rhesis")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert 'When creating a new branch, always branch from the latest `main` to avoid conflicts:' in text, "expected to find: " + 'When creating a new branch, always branch from the latest `main` to avoid conflicts:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert 'git checkout -b feature/your-feature-name' in text, "expected to find: " + 'git checkout -b feature/your-feature-name'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/pull-requests.mdc')
    assert '# Ensure you have the latest main' in text, "expected to find: " + '# Ensure you have the latest main'[:80]

