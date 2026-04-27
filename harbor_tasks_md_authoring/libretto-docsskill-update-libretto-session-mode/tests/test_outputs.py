"""Behavioral checks for libretto-docsskill-update-libretto-session-mode (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/libretto")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert 'Sessions start in **read-only mode** by default. **Every time you launch a browser — whether via `open` or `run` — you MUST immediately announce the session mode.** This is non-negotiable. Do NOT skip' in text, "expected to find: " + 'Sessions start in **read-only mode** by default. **Every time you launch a browser — whether via `open` or `run` — you MUST immediately announce the session mode.** This is non-negotiable. Do NOT skip'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert "> I've opened the browser in **read-only mode**. I can observe the page, take snapshots, and inspect network traffic, but I **cannot** click, type, fill forms, submit, or execute any actions that modi" in text, "expected to find: " + "> I've opened the browser in **read-only mode**. I can observe the page, take snapshots, and inspect network traffic, but I **cannot** click, type, fill forms, submit, or execute any actions that modi"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/libretto/SKILL.md')
    assert "> If you'd like me to interact with elements (clicking buttons, filling forms, submitting data, scrolling, or making network requests), let me know and I'll switch to **full-access mode**." in text, "expected to find: " + "> If you'd like me to interact with elements (clicking buttons, filling forms, submitting data, scrolling, or making network requests), let me know and I'll switch to **full-access mode**."[:80]

