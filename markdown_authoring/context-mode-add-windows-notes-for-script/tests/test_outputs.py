"""Behavioral checks for context-mode-add-windows-notes-for-script (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/context-mode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('configs/codex/AGENTS.md')
    assert 'cmdlets (`Format-List`, `Format-Table`, `Get-Culture`, etc.) do not exist in bash and will fail' in text, "expected to find: " + 'cmdlets (`Format-List`, `Format-Table`, `Get-Culture`, etc.) do not exist in bash and will fail'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('configs/codex/AGENTS.md')
    assert '**Relative paths** — The sandbox CWD is a temp directory, not your project root. Always convert' in text, "expected to find: " + '**Relative paths** — The sandbox CWD is a temp directory, not your project root. Always convert'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('configs/codex/AGENTS.md')
    assert '**Windows drive letter paths** — The sandbox runs Git Bash / MSYS2, not WSL. Drive letters must' in text, "expected to find: " + '**Windows drive letter paths** — The sandbox runs Git Bash / MSYS2, not WSL. Drive letters must'[:80]

