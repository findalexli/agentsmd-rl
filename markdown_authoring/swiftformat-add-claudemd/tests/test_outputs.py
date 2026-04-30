"""Behavioral checks for swiftformat-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/swiftformat")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Define local helpers** in extensions on `Formatter` at the bottom of the rule file. Mark them `internal` for discoverability. Move helpers used by multiple rules to `ParsingHelpers.swift`. Parsing' in text, "expected to find: " + '- **Define local helpers** in extensions on `Formatter` at the bottom of the rule file. Mark them `internal` for discoverability. Move helpers used by multiple rules to `ParsingHelpers.swift`. Parsing'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**Note:** Do not modify `Rules.md` directly. It's auto-generated when running the test suite. `MetadataTests` may fail after adding a new rule; re-run after metadata regenerates." in text, "expected to find: " + "**Note:** Do not modify `Rules.md` directly. It's auto-generated when running the test suite. `MetadataTests` may fail after adding a new rule; re-run after metadata regenerates."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use `exclude: [.someRule]` if another rule conflicts with your test case. However, only exclude a rule from a test case if the test case would fail otherwise.' in text, "expected to find: " + '- Use `exclude: [.someRule]` if another rule conflicts with your test case. However, only exclude a rule from a test case if the test case would fail otherwise.'[:80]

