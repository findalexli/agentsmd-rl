"""Behavioral checks for agent-rules-fix-nested-code-block-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-rules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/swift6-migration.mdc')
    assert 'This project is licensed under the Apache License, Version 2.0.' in text, "expected to find: " + 'This project is licensed under the Apache License, Version 2.0.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/swift6-migration.mdc')
    assert 'See: https://www.apache.org/licenses/LICENSE-2.0' in text, "expected to find: " + 'See: https://www.apache.org/licenses/LICENSE-2.0'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('project-rules/continuous-improvement.mdc')
    assert '````markdown' in text, "expected to find: " + '````markdown'[:80]

