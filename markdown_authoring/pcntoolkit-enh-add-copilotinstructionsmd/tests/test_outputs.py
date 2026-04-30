"""Behavioral checks for pcntoolkit-enh-add-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pcntoolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'house rules (style, commits), and avoid common pitfalls. When you create new code or change old code you MUST explain everything you do clearly and simply for the developer to understand, and you MUST' in text, "expected to find: " + 'house rules (style, commits), and avoid common pitfalls. When you create new code or change old code you MUST explain everything you do clearly and simply for the developer to understand, and you MUST'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Feature branches merged via PRs to the dev branch. Only when dev branch is stable, merge to master and tag for release.' in text, "expected to find: " + '- Feature branches merged via PRs to the dev branch. Only when dev branch is stable, merge to master and tag for release.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Use NumPy-style `Parameters`, `Returns`, `Raises` sections in the docstrings' in text, "expected to find: " + '- Use NumPy-style `Parameters`, `Returns`, `Raises` sections in the docstrings'[:80]

