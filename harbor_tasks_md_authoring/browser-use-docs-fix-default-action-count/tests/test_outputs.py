"""Behavioral checks for browser-use-docs-fix-default-action-count (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/browser-use")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '* `max_actions_per_step` (default: `3`): Maximum actions per step, e.g. for form filling the agent can output 3 fields at once. We execute the actions until the page changes.' in text, "expected to find: " + '* `max_actions_per_step` (default: `3`): Maximum actions per step, e.g. for form filling the agent can output 3 fields at once. We execute the actions until the page changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "We're excited to have you join our community of contributors." in text, "expected to find: " + "We're excited to have you join our community of contributors."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'history.screenshot_paths()        # List of screenshot paths' in text, "expected to find: " + 'history.screenshot_paths()        # List of screenshot paths'[:80]

