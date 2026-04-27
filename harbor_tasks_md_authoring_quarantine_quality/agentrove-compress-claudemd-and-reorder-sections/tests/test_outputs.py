"""Behavioral checks for agentrove-compress-claudemd-and-reorder-sections (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentrove")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- When query keys include optional dimensions (e.g., `cwd`), add a separate prefix key without the optional dimension for broad invalidation (e.g., `gitBranchesAll: (id) => ['sandbox', id, 'git-branch" in text, "expected to find: " + "- When query keys include optional dimensions (e.g., `cwd`), add a separate prefix key without the optional dimension for broad invalidation (e.g., `gitBranchesAll: (id) => ['sandbox', id, 'git-branch"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `useEffect` cleanup closures must not rely on hook-scoped utilities that close over the current entity ID when cleanup may serve sessions from a different entity — use refs or the underlying API (e.' in text, "expected to find: " + '- `useEffect` cleanup closures must not rely on hook-scoped utilities that close over the current entity ID when cleanup may serve sessions from a different entity — use refs or the underlying API (e.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- When invalidating a React Query key built from an identifier, verify the format matches consumers' — cwd-relative vs workspace-root-relative paths miss each other; when formats can diverge, invalida" in text, "expected to find: " + "- When invalidating a React Query key built from an identifier, verify the format matches consumers' — cwd-relative vs workspace-root-relative paths miss each other; when formats can diverge, invalida"[:80]

