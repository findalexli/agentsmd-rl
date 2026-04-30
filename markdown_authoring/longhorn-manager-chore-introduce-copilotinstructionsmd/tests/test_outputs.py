"""Behavioral checks for longhorn-manager-chore-introduce-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/longhorn-manager")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- If issue details are unavailable, report `Issue context unavailable` and perform a partial review limited to code correctness only. Do not assess issue alignment.' in text, "expected to find: " + '- If issue details are unavailable, report `Issue context unavailable` and perform a partial review limited to code correctness only. Do not assess issue alignment.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The issue context is improving replica rebuild performance under high I/O. The PR includes changes to replica_manager.go and spdk_io.go.' in text, "expected to find: " + 'The issue context is improving replica rebuild performance under high I/O. The PR includes changes to replica_manager.go and spdk_io.go.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Partially aligned — the PR improves I/O throughput but does not address edge cases for concurrent rebuilds mentioned in the issue.' in text, "expected to find: " + 'Partially aligned — the PR improves I/O throughput but does not address edge cases for concurrent rebuilds mentioned in the issue.'[:80]

