"""Behavioral checks for dotfiles-crabfitcli-use-installed-binary-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotfiles")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('pkgs/crabfit-cli/SKILL.md')
    assert 'crabfit-cli respond EVENT_ID --name "Bob" --slots 1000-19012026 1100-19012026' in text, "expected to find: " + 'crabfit-cli respond EVENT_ID --name "Bob" --slots 1000-19012026 1100-19012026'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('pkgs/crabfit-cli/SKILL.md')
    assert 'crabfit-cli create --name "Project Sync" --dates +1:+5 --start 10 --end 16' in text, "expected to find: " + 'crabfit-cli create --name "Project Sync" --dates +1:+5 --start 10 --end 16'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('pkgs/crabfit-cli/SKILL.md')
    assert 'crabfit-cli create --name "Team Meeting" --dates 2026-01-20,2026-01-22' in text, "expected to find: " + 'crabfit-cli create --name "Team Meeting" --dates 2026-01-20,2026-01-22'[:80]

