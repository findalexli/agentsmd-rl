"""Behavioral checks for ragflow-choreclaudemd-add-shared-ui-component (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ragflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('web/CLAUDE.md')
    assert "The folder `src/components/ui/` is the project's **shared UI library** — it contains both official shadcn/ui primitives and project-authored common components built on top of shadcn. Both kinds are in" in text, "expected to find: " + "The folder `src/components/ui/` is the project's **shared UI library** — it contains both official shadcn/ui primitives and project-authored common components built on top of shadcn. Both kinds are in"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('web/CLAUDE.md')
    assert '- If a component does not meet requirements, **wrap or compose it** in a new component **outside** `src/components/ui/` (e.g., under `src/components/` or a feature folder), and customize via `classNam' in text, "expected to find: " + '- If a component does not meet requirements, **wrap or compose it** in a new component **outside** `src/components/ui/` (e.g., under `src/components/` or a feature folder), and customize via `classNam'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('web/CLAUDE.md')
    assert '- Adding a new shared component to `src/components/ui/`, or upgrading a shadcn primitive via the official `shadcn` CLI, is allowed only when the user explicitly requests it.' in text, "expected to find: " + '- Adding a new shared component to `src/components/ui/`, or upgrading a shadcn primitive via the official `shadcn` CLI, is allowed only when the user explicitly requests it.'[:80]

