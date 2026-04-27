"""Behavioral checks for vibesos-docsclaudemd-document-generate-flow-routing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibesos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "The real flow: the editor sends a `{ type: 'generate', ... }` WebSocket message, which is handled in `scripts/server/ws.ts` at `case 'generate':` (around line 328). That branch wraps the user's prompt" in text, "expected to find: " + "The real flow: the editor sends a `{ type: 'generate', ... }` WebSocket message, which is handled in `scripts/server/ws.ts` at `case 'generate':` (around line 328). That branch wraps the user's prompt"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Direction D's staged-preview events (`generation_stage` / `preview_reload` / `reference_preview`) are emitted by the bridge's stream parser, gated by `turnMode === 'generate'`, so they fire on the rea" in text, "expected to find: " + "Direction D's staged-preview events (`generation_stage` / `preview_reload` / `reference_preview`) are emitted by the bridge's stream parser, gated by `turnMode === 'generate'`, so they fire on the rea"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Chat iteration (`case 'chat':`) uses the same bridge — so the bridge's per-turn state needs to be reset between generate and chat turns. That's what `bridge.setTurnMode('generate' | 'chat', initialSta" in text, "expected to find: " + "Chat iteration (`case 'chat':`) uses the same bridge — so the bridge's per-turn state needs to be reset between generate and chat turns. That's what `bridge.setTurnMode('generate' | 'chat', initialSta"[:80]

