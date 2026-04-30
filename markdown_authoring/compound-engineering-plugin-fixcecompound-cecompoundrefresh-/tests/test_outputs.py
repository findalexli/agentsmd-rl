"""Behavioral checks for compound-engineering-plugin-fixcecompound-cecompoundrefresh- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert '> Also scan the "user\'s auto-memory" block injected into your system prompt (Claude Code only). Check for notes related to the learning\'s problem domain. Report any memory-sourced drift signals separa' in text, "expected to find: " + '> Also scan the "user\'s auto-memory" block injected into your system prompt (Claude Code only). Check for notes related to the learning\'s problem domain. Report any memory-sourced drift signals separa'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md')
    assert '- **Auto memory** (Claude Code only) — does the injected auto-memory block in your system prompt contain entries in the same problem domain? Scan that block directly. If the block is absent, skip this' in text, "expected to find: " + '- **Auto memory** (Claude Code only) — does the injected auto-memory block in your system prompt contain entries in the same problem domain? Scan that block directly. If the block is absent, skip this'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '1. **Extract from conversation**: Identify the problem and solution from conversation history. Also scan the "user\'s auto-memory" block injected into your system prompt, if present (Claude Code only) ' in text, "expected to find: " + '1. **Extract from conversation**: Identify the problem and solution from conversation history. Also scan the "user\'s auto-memory" block injected into your system prompt, if present (Claude Code only) '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '1. Look for a block labeled "user\'s auto-memory" (Claude Code only) already present in your system prompt context — MEMORY.md\'s entries are inlined there' in text, "expected to find: " + '1. Look for a block labeled "user\'s auto-memory" (Claude Code only) already present in your system prompt context — MEMORY.md\'s entries are inlined there'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert 'Before launching Phase 1 subagents, check the auto-memory block injected into your system prompt for notes relevant to the problem being documented.' in text, "expected to find: " + 'Before launching Phase 1 subagents, check the auto-memory block injected into your system prompt for notes relevant to the problem being documented.'[:80]

