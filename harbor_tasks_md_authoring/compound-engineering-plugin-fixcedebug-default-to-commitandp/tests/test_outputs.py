"""Behavioral checks for compound-engineering-plugin-fixcedebug-default-to-commitandp (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert "1. **Check for contextual overrides first.** Look at the user's original prompt, loaded memories, and the user/repo `AGENTS.md` or `CLAUDE.md` for preferences that conflict with auto commit-and-PR — f" in text, "expected to find: " + "1. **Check for contextual overrides first.** Look at the user's original prompt, loaded memories, and the user/repo `AGENTS.md` or `CLAUDE.md` for preferences that conflict with auto commit-and-PR — f"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert "Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini, `ask_user` in Pi (requires the `pi-ask-user` extension)). In Claude Co" in text, "expected to find: " + "Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini, `ask_user` in Pi (requires the `pi-ask-user` extension)). In Claude Co"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert '3. **Run `/ce-commit-push-pr`.** When the entry came from an issue tracker, include the appropriate auto-close syntax for that tracker in the location it requires — most trackers parse PR descriptions' in text, "expected to find: " + '3. **Run `/ce-commit-push-pr`.** When the entry came from an issue tracker, include the appropriate auto-close syntax for that tracker in the location it requires — most trackers parse PR descriptions'[:80]

