"""Behavioral checks for sonarjs-js1033-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sonarjs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**Important for Claude:** Do not run full unit tests (`npm run bridge:test`) or ruling tests (`npm run ruling`) as they take a long time to complete. Run only specific tests for the rules you're worki" in text, "expected to find: " + "**Important for Claude:** Do not run full unit tests (`npm run bridge:test`) or ruling tests (`npm run ruling`) as they take a long time to complete. Run only specific tests for the rules you're worki"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Keep this file up to date:** When making changes to build processes, project structure, or development workflows, update this file accordingly' in text, "expected to find: " + '- **Keep this file up to date:** When making changes to build processes, project structure, or development workflows, update this file accordingly'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| RuleTester                 | Parser                             | Use When                                    |' in text, "expected to find: " + '| RuleTester                 | Parser                             | Use When                                    |'[:80]

