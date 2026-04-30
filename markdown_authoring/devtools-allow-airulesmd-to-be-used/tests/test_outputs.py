"""Behavioral checks for devtools-allow-airulesmd-to-be-used (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/devtools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ai_rules.mdc')
    assert 'description: Apply rules from AI_RULES.md to all interactions.' in text, "expected to find: " + 'description: Apply rules from AI_RULES.md to all interactions.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ai_rules.mdc')
    assert 'Follow the rules defined in [AI_RULES.md](../../AI_RULES.md).' in text, "expected to find: " + 'Follow the rules defined in [AI_RULES.md](../../AI_RULES.md).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/ai_rules.mdc')
    assert 'alwaysApply: true' in text, "expected to find: " + 'alwaysApply: true'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Refer to the shared [AI Rules](AI_RULES.md) for guidelines when working in this repository.' in text, "expected to find: " + 'Refer to the shared [AI Rules](AI_RULES.md) for guidelines when working in this repository.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '# Claude Code Guidelines' in text, "expected to find: " + '# Claude Code Guidelines'[:80]

