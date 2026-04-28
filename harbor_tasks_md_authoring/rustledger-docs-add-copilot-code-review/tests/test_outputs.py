"""Behavioral checks for rustledger-docs-add-copilot-code-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rustledger")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This triggers a fresh review against the current diff. Copilot leaves "Comment" reviews (never approves or blocks merging).' in text, "expected to find: " + 'This triggers a fresh review against the current diff. Copilot leaves "Comment" reviews (never approves or blocks merging).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Request or re-request a Copilot review on any PR:' in text, "expected to find: " + 'Request or re-request a Copilot review on any PR:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'gh pr edit <PR_NUMBER> --add-reviewer @copilot' in text, "expected to find: " + 'gh pr edit <PR_NUMBER> --add-reviewer @copilot'[:80]

