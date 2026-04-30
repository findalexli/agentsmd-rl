"""Behavioral checks for mudblazor-build-improve-docs-guidance-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mudblazor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Show code for simple, canonical examples by default. Also show code when the markup, binding, accessibility attribute, or event pattern is the behavior being taught. Collapse examples longer than 15' in text, "expected to find: " + '- Show code for simple, canonical examples by default. Also show code when the markup, binding, accessibility attribute, or event pattern is the behavior being taught. Collapse examples longer than 15'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Include practical guidance near the relevant example for accessibility-sensitive behavior, keyboard interaction, focus management, and other usage constraints. When prose mentions an accessibility r' in text, "expected to find: " + '- Include practical guidance near the relevant example for accessibility-sensitive behavior, keyboard interaction, focus management, and other usage constraints. When prose mentions an accessibility r'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Keep examples in `src/MudBlazor.Docs/Pages/Components/<ComponentName>/Examples/` and name them after the component and scenario, such as `<ComponentName>SimpleExample`, `<ComponentName>DenseExample`' in text, "expected to find: " + '- Keep examples in `src/MudBlazor.Docs/Pages/Components/<ComponentName>/Examples/` and name them after the component and scenario, such as `<ComponentName>SimpleExample`, `<ComponentName>DenseExample`'[:80]

