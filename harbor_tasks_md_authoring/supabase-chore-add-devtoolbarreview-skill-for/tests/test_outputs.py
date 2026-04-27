"""Behavioral checks for supabase-chore-add-devtoolbarreview-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/supabase")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/dev-toolbar-review/SKILL.md')
    assert '- **Runtime guards** in components: `IS_LOCAL_DEV` checks — `DevToolbar` and `DevToolbarTrigger` return `null` to hide themselves, while `DevToolbarProvider` passes children through (`<>{children}</>`' in text, "expected to find: " + '- **Runtime guards** in components: `IS_LOCAL_DEV` checks — `DevToolbar` and `DevToolbarTrigger` return `null` to hide themselves, while `DevToolbarProvider` passes children through (`<>{children}</>`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/dev-toolbar-review/SKILL.md')
    assert "- **Build-time tree-shaking** in `index.ts`: `process.env.NODE_ENV !== 'development'` ternaries that replace components with noops/stubs so the implementation is eliminated from production bundles." in text, "expected to find: " + "- **Build-time tree-shaking** in `index.ts`: `process.env.NODE_ENV !== 'development'` ternaries that replace components with noops/stubs so the implementation is eliminated from production bundles."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/dev-toolbar-review/SKILL.md')
    assert '- Changes to `emitToDevListeners` or `subscribeToEvents` that could introduce side effects on the actual capture path (e.g., throwing errors, blocking, mutating event data)' in text, "expected to find: " + '- Changes to `emitToDevListeners` or `subscribeToEvents` that could introduce side effects on the actual capture path (e.g., throwing errors, blocking, mutating event data)'[:80]

