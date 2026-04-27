"""Behavioral checks for phidata-chore-update-claudemd-ci-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phidata")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Every non-draft PR automatically receives a review from Opus using both `code-review` and `pr-review-toolkit` official plugins (10 specialized agents total). No manual trigger needed — the review post' in text, "expected to find: " + 'Every non-draft PR automatically receives a review from Opus using both `code-review` and `pr-review-toolkit` official plugins (10 specialized agents total). No manual trigger needed — the review post'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When running in GitHub Actions (CI), always end your response with a plain-text summary of findings. Never let the final action be a tool call. If there are no issues, say "No high-confidence findings' in text, "expected to find: " + 'When running in GitHub Actions (CI), always end your response with a plain-text summary of findings. Never let the final action be a tool call. If there are no issues, say "No high-confidence findings'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Both sync and async variants exist for all new public methods' in text, "expected to find: " + '- Both sync and async variants exist for all new public methods'[:80]

