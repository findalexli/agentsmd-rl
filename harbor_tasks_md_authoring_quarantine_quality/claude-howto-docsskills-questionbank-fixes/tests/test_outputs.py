"""Behavioral checks for claude-howto-docsskills-questionbank-fixes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-howto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lesson-quiz/references/question-bank.md')
    assert '- **Explanation**: Skill metadata occupies about 1% of the context window (fallback: 8,000 characters). This is configurable with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.' in text, "expected to find: " + '- **Explanation**: Skill metadata occupies about 1% of the context window (fallback: 8,000 characters). This is configurable with `SLASH_COMMAND_TOOL_CHAR_BUDGET`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lesson-quiz/references/question-bank.md')
    assert '- **Explanation**: CLI-defined agents (`--agents` flag) override Project-level (`.claude/agents/`), which override User-level (`~/.claude/agents/`).' in text, "expected to find: " + '- **Explanation**: CLI-defined agents (`--agents` flag) override Project-level (`.claude/agents/`), which override User-level (`~/.claude/agents/`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/lesson-quiz/references/question-bank.md')
    assert '- **Options**: A) Project > User > CLI | B) CLI > Project > User | C) User > Project > CLI | D) They all have equal priority' in text, "expected to find: " + '- **Options**: A) Project > User > CLI | B) CLI > Project > User | C) User > Project > CLI | D) They all have equal priority'[:80]

