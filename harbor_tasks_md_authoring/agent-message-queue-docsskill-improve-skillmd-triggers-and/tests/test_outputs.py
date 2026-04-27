"""Behavioral checks for agent-message-queue-docsskill-improve-skillmd-triggers-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-message-queue")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co' in text, "expected to find: " + 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)' in text, "expected to find: " + '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/amq-cli/SKILL.md')
    assert '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents' in text, "expected to find: " + '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co' in text, "expected to find: " + 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)' in text, "expected to find: " + '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/amq-cli/SKILL.md')
    assert '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents' in text, "expected to find: " + '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co' in text, "expected to find: " + 'description: Coordinate agents via the AMQ CLI for file-based inter-agent messaging. Use when you need to send messages to another agent (Claude/Codex), receive messages from partner agents, set up co'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)' in text, "expected to find: " + '- `references/message-format.md` — Read when you need the full frontmatter schema (all fields, types, defaults)'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents' in text, "expected to find: " + '- `references/coop-mode.md` — Read when setting up or debugging co-op workflows between agents'[:80]

