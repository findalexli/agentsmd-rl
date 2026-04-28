"""Behavioral checks for vrc-get-dev-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vrc-get")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- After completing code and commit, please add changelog entry. please note that the numbers in the changelog file is pull request number, not a issue number.' in text, "expected to find: " + '- After completing code and commit, please add changelog entry. please note that the numbers in the changelog file is pull request number, not a issue number.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- Please don't make localization for locales other than en / ja. I cannot review those locales." in text, "expected to find: " + "- Please don't make localization for locales other than en / ja. I cannot review those locales."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Run cargo clippy for lints and cargo fmt for format before commit.' in text, "expected to find: " + '- Run cargo clippy for lints and cargo fmt for format before commit.'[:80]

