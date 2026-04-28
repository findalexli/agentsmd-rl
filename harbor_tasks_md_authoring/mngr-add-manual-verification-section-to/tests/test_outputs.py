"""Behavioral checks for mngr-add-manual-verification-section-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mngr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'For interactive components (TUIs, interactive prompts, etc.), use `tmux send-keys` and `tmux capture-pane` to manually verify them. This is a special case: do NOT crystallize these into pytest tests. ' in text, "expected to find: " + 'For interactive components (TUIs, interactive prompts, etc.), use `tmux send-keys` and `tmux capture-pane` to manually verify them. This is a special case: do NOT crystallize these into pytest tests. '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Before declaring any feature complete, manually verify it: exercise the feature exactly as a real user would, with real inputs, and critically evaluate whether it *actually does the right thing*. Do n' in text, "expected to find: " + 'Before declaring any feature complete, manually verify it: exercise the feature exactly as a real user would, with real inputs, and critically evaluate whether it *actually does the right thing*. Do n'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Note that "uv run pytest" defaults to running all "unit" and "integration" tests, but the "acceptance" tests also run in CI. Do *not* run the acceptance tests locally to validate changes--always all' in text, "expected to find: " + '- Note that "uv run pytest" defaults to running all "unit" and "integration" tests, but the "acceptance" tests also run in CI. Do *not* run the acceptance tests locally to validate changes--always all'[:80]

