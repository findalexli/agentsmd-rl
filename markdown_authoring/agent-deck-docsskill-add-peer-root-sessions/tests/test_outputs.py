"""Behavioral checks for agent-deck-docsskill-add-peer-root-sessions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-deck")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-deck/SKILL.md')
    assert '**The default — sub-agent linkage:** `agent-deck launch` and `agent-deck add`, when invoked from *inside* an existing agent-deck session, automatically link the new session as a child of the calling s' in text, "expected to find: " + '**The default — sub-agent linkage:** `agent-deck launch` and `agent-deck add`, when invoked from *inside* an existing agent-deck session, automatically link the new session as a child of the calling s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-deck/SKILL.md')
    assert '**When the default is wrong — root-level peer sessions:** if you are creating a session that should stand independently at the root — a peer conductor, a standalone project session, a session that sho' in text, "expected to find: " + '**When the default is wrong — root-level peer sessions:** if you are creating a session that should stand independently at the root — a peer conductor, a standalone project session, a session that sho'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-deck/SKILL.md')
    assert '**Note on the launch-subagent.sh script:** that script is specifically designed to create sub-agents (the name says so). It does NOT support `-no-parent`. For peer sessions, skip the script and invoke' in text, "expected to find: " + '**Note on the launch-subagent.sh script:** that script is specifically designed to create sub-agents (the name says so). It does NOT support `-no-parent`. For peer sessions, skip the script and invoke'[:80]

