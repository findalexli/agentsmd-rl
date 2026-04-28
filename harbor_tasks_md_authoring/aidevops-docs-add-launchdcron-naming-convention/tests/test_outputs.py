"""Behavioral checks for aidevops-docs-add-launchdcron-naming-convention (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aidevops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert "When creating launchd plists or cron jobs, use the `aidevops` prefix so they're easy to find in System Settings > General > Login Items & Extensions:" in text, "expected to find: " + "When creating launchd plists or cron jobs, use the `aidevops` prefix so they're easy to find in System Settings > General > Login Items & Extensions:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '- **launchd label**: `sh.aidevops.<name>` (reverse domain, e.g., `sh.aidevops.session-miner-pulse`)' in text, "expected to find: " + '- **launchd label**: `sh.aidevops.<name>` (reverse domain, e.g., `sh.aidevops.session-miner-pulse`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '- **plist filename**: `sh.aidevops.<name>.plist`' in text, "expected to find: " + '- **plist filename**: `sh.aidevops.<name>.plist`'[:80]

