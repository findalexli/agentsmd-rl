"""Behavioral checks for elasticsearch-js-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/elasticsearch-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'All code in `src/` and `test/`, and any scripts run by `npm` that are defined in package.json, must be runnable with equivalent results on Linux, MacOS and Windows. For example, running the following ' in text, "expected to find: " + 'All code in `src/` and `test/`, and any scripts run by `npm` that are defined in package.json, must be runnable with equivalent results on Linux, MacOS and Windows. For example, running the following '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If a specific action you learned to do better will be useful to other agents doing the same task in the future, but may not be needed for ALL agent-related tasks, create or update skills in `.github/s' in text, "expected to find: " + 'If a specific action you learned to do better will be useful to other agents doing the same task in the future, but may not be needed for ALL agent-related tasks, create or update skills in `.github/s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'If you learned something that will be useful to any contributor to this project, update `AGENTS.md`.' in text, "expected to find: " + 'If you learned something that will be useful to any contributor to this project, update `AGENTS.md`.'[:80]

