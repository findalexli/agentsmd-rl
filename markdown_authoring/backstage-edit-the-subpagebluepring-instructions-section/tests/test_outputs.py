"""Behavioral checks for backstage-edit-the-subpagebluepring-instructions-section (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/backstage")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md')
    assert 'Old frontend plugins often use React Router `<Route>` trees inside a router component to handle internal navigation. Before migrating, determine which routing pattern fits the plugin.' in text, "expected to find: " + 'Old frontend plugins often use React Router `<Route>` trees inside a router component to handle internal navigation. Before migrating, determine which routing pattern fits the plugin.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md')
    assert '> "Does your plugin use top-level tabs that users navigate between via a header (e.g. Overview / Settings)? Or does it use detail/drill-down routes (e.g. `/my-plugin/items/:id`)?"' in text, "expected to find: " + '> "Does your plugin use top-level tabs that users navigate between via a header (e.g. Overview / Settings)? Or does it use detail/drill-down routes (e.g. `/my-plugin/items/:id`)?"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/.well-known/skills/plugin-full-frontend-system-migration/SKILL.md')
    assert '**If the plugin uses drill-down routing only**, use a `PageBlueprint` with a `loader` that handles its own `<Routes>` and skip the rest of this step:' in text, "expected to find: " + '**If the plugin uses drill-down routing only**, use a `PageBlueprint` with a `loader` that handles its own `<Routes>` and skip the rest of this step:'[:80]

