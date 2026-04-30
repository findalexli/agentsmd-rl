"""Behavioral checks for isaaclab-forbid-pushing-to-origin-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/isaaclab")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Never push to `origin` (`isaac-sim/IsaacLab`).** The `origin` remote is the public upstream repository. Push to your own fork remote (e.g., `antoine`, `alex`) or to the remote of the PR you are wo' in text, "expected to find: " + '- **Never push to `origin` (`isaac-sim/IsaacLab`).** The `origin` remote is the public upstream repository. Push to your own fork remote (e.g., `antoine`, `alex`) or to the remote of the PR you are wo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "7. Verify pre-commit still passes before pushing — never push commits that haven't been checked" in text, "expected to find: " + "7. Verify pre-commit still passes before pushing — never push commits that haven't been checked"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**CRITICAL: Always run pre-commit hooks BEFORE committing and BEFORE pushing.**' in text, "expected to find: " + '**CRITICAL: Always run pre-commit hooks BEFORE committing and BEFORE pushing.**'[:80]

