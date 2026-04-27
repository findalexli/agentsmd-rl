"""Behavioral checks for agent-deck-docsskill-add-known-gotchas-section (markdown_authoring task).

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
    assert "If `~/.agent-deck/skills/sources.toml` (or other config files) were copied verbatim from a macOS machine, paths like `/Users/<name>/` won't exist on Linux (should be `/home/<user>/`). The symptom: `ag" in text, "expected to find: " + "If `~/.agent-deck/skills/sources.toml` (or other config files) were copied verbatim from a macOS machine, paths like `/Users/<name>/` won't exist on Linux (should be `/home/<user>/`). The symptom: `ag"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-deck/SKILL.md')
    assert 'The `channels` field persists and every `session start` / `session restart` rebuilds the claude invocation with `--channels`. Do NOT rely on `.mcp.json` telegram entries — those load the plugin as a r' in text, "expected to find: " + 'The `channels` field persists and every `session start` / `session restart` rebuilds the claude invocation with `--channels`. Do NOT rely on `.mcp.json` telegram entries — those load the plugin as a r'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-deck/SKILL.md')
    assert "**Note — v1.7.0 display bug:** `agent-deck session show --json <id>` currently omits the `channels` field (fix pending). `agent-deck list --json | jq '.[] | select(.id==<id>)'` shows it correctly. Dat" in text, "expected to find: " + "**Note — v1.7.0 display bug:** `agent-deck session show --json <id>` currently omits the `channels` field (fix pending). `agent-deck list --json | jq '.[] | select(.id==<id>)'` shows it correctly. Dat"[:80]

