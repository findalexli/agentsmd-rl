"""Behavioral checks for classicy-docs-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/classicy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **ClassicyAppManagerProvider** (`src/SystemFolder/ControlPanels/AppManager/ClassicyAppManagerContext.tsx`) - Root provider that wraps SoundManager and Analytics' in text, "expected to find: " + '- **ClassicyAppManagerProvider** (`src/SystemFolder/ControlPanels/AppManager/ClassicyAppManagerContext.tsx`) - Root provider that wraps SoundManager and Analytics'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "Classicy is a React/TypeScript UI framework that replicates the Mac OS 8 (Platinum) interface. It's distributed as an npm package with ES and UMD module formats." in text, "expected to find: " + "Classicy is a React/TypeScript UI framework that replicates the Mac OS 8 (Platinum) interface. It's distributed as an npm package with ES and UMD module formats."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `src/SystemFolder/ControlPanels/` - System-level managers (AppManager, SoundManager, AppearanceManager, DateAndTimeManager)' in text, "expected to find: " + '- `src/SystemFolder/ControlPanels/` - System-level managers (AppManager, SoundManager, AppearanceManager, DateAndTimeManager)'[:80]

