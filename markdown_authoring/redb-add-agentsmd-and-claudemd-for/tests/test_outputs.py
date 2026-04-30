"""Behavioral checks for redb-add-agentsmd-and-claudemd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/redb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The CI workflow pins specific versions; prefer those versions if you hit incompatibilities. See' in text, "expected to find: " + 'The CI workflow pins specific versions; prefer those versions if you hit incompatibilities. See'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Always run `just test` and confirm it passes before telling the user you are done.**' in text, "expected to find: " + '**Always run `just test` and confirm it passes before telling the user you are done.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This target runs the `pre` recipe first, which executes `cargo deny check licenses`,' in text, "expected to find: " + 'This target runs the `pre` recipe first, which executes `cargo deny check licenses`,'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Read `AGENTS.md` for repository-specific agent instructions.' in text, "expected to find: " + 'Read `AGENTS.md` for repository-specific agent instructions.'[:80]

