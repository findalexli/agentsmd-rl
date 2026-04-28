"""Behavioral checks for lynx-infra-add-agentsmd-for-commit (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lynx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Module or subsystem name (e.g., `Clay`, `Layout`, `Headers`, `Painting`, `Harmony`, `Android`, `iOS`, etc.), optional but recommended.' in text, "expected to find: " + '- Module or subsystem name (e.g., `Clay`, `Layout`, `Headers`, `Painting`, `Harmony`, `Android`, `iOS`, etc.), optional but recommended.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `Feature`, `BugFix`, `Optimize`, `Refactor`, `Infra`, `Docs`, `Test`, etc., using capitalized English.' in text, "expected to find: " + '- `Feature`, `BugFix`, `Optimize`, `Refactor`, `Infra`, `Docs`, `Test`, etc., using capitalized English.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- All commit messages MUST be written in **English**.' in text, "expected to find: " + '- All commit messages MUST be written in **English**.'[:80]

