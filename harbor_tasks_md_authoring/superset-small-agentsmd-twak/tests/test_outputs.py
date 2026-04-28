"""Behavioral checks for superset-small-agentsmd-twak (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/superset")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `packages/ui` - Shared UI components (shadcn/ui + TailwindCSS v4).' in text, "expected to find: " + '- `packages/ui` - Shared UI components (shadcn/ui + TailwindCSS v4).'[:80]

