"""Behavioral checks for chrome-devtools-mcp-docstroubleshooting-add-symptom-for-miss (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chrome-devtools-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/troubleshooting/SKILL.md')
    assert 'All tools in `chrome-devtools-mcp` are annotated with `readOnlyHint: true` (for safe, non-modifying tools) or `readOnlyHint: false` (for tools that modify browser state, like `emulate`, `click`, `navi' in text, "expected to find: " + 'All tools in `chrome-devtools-mcp` are annotated with `readOnlyHint: true` (for safe, non-modifying tools) or `readOnlyHint: false` (for tools that modify browser state, like `emulate`, `click`, `navi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/troubleshooting/SKILL.md')
    assert 'If the server starts successfully but only a limited subset of tools (like `list_pages`, `get_console_message`, `lighthouse_audit`, `take_memory_snapshot`) are available, this is likely because the MC' in text, "expected to find: " + 'If the server starts successfully but only a limited subset of tools (like `list_pages`, `get_console_message`, `lighthouse_audit`, `take_memory_snapshot`) are available, this is likely because the MC'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/troubleshooting/SKILL.md')
    assert '#### Symptom: Missing Tools / Only 9 tools available' in text, "expected to find: " + '#### Symptom: Missing Tools / Only 9 tools available'[:80]

