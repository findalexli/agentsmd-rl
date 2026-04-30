"""Behavioral checks for spawn-chorexengage-drop-disclosure-line-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/x-engage-prompt.md')
    assert '- **NO disclosure line.** Do not add "(disclosure: i help build this)" or any similar attribution. Post the reply as-is.' in text, "expected to find: " + '- **NO disclosure line.** Do not add "(disclosure: i help build this)" or any similar attribution. Post the reply as-is.'[:80]

