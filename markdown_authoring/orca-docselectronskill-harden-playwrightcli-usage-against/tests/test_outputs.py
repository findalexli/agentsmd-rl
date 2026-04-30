"""Behavioral checks for orca-docselectronskill-harden-playwrightcli-usage-against (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/orca")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron/SKILL.md')
    assert 'command playwright-cli eval "(() => { const s = window.__store?.getState(); const wtId = s.activeWorktreeId; s.openFile({ worktreeId: wtId, filePath: \'/path/to/file\', relativePath: \'file.ts\', mode: \'e' in text, "expected to find: " + 'command playwright-cli eval "(() => { const s = window.__store?.getState(); const wtId = s.activeWorktreeId; s.openFile({ worktreeId: wtId, filePath: \'/path/to/file\', relativePath: \'file.ts\', mode: \'e'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron/SKILL.md')
    assert 'command playwright-cli eval "(() => { const s = window.__store?.getState(); return JSON.stringify({ activeWorktreeId: s.activeWorktreeId, activeTabId: s.activeTabId, activeFileId: s.activeFileId, acti' in text, "expected to find: " + 'command playwright-cli eval "(() => { const s = window.__store?.getState(); return JSON.stringify({ activeWorktreeId: s.activeWorktreeId, activeTabId: s.activeTabId, activeFileId: s.activeFileId, acti'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/electron/SKILL.md')
    assert "Use `command playwright-cli …` to bypass shell aliases (e.g. `alias playwright-cli='playwright-cli --persistent'`) that leak flags into subcommands. Behaves identically when no alias is set. All examp" in text, "expected to find: " + "Use `command playwright-cli …` to bypass shell aliases (e.g. `alias playwright-cli='playwright-cli --persistent'`) that leak flags into subcommands. Behaves identically when no alias is set. All examp"[:80]

