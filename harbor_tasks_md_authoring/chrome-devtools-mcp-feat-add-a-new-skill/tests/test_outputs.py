"""Behavioral checks for chrome-devtools-mcp-feat-add-a-new-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/chrome-devtools-mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert '**Accessibility Tree vs DOM**: Visually hiding an element (e.g., `CSS opacity: 0`) behaves differently for screen readers than `display: none` or `aria-hidden="true"`. The `take_snapshot` tool returns' in text, "expected to find: " + '**Accessibility Tree vs DOM**: Visually hiding an element (e.g., `CSS opacity: 0`) behaves differently for screen readers than `display: none` or `aria-hidden="true"`. The `take_snapshot` tool returns'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert '**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https' in text, "expected to find: " + '**Reading web.dev documentation**: If you need to research specific accessibility guidelines (like `https://web.dev/articles/accessible-tap-targets`), you can append `.md.txt` to the URL (e.g., `https'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/a11y-debugging/SKILL.md')
    assert '- **Visual Inspection**: If automated scripts cannot determine contrast (e.g., text over gradient images or complex backgrounds), use `take_screenshot` to capture the element. While models cannot meas' in text, "expected to find: " + '- **Visual Inspection**: If automated scripts cannot determine contrast (e.g., text over gradient images or complex backgrounds), use `take_screenshot` to capture the element. While models cannot meas'[:80]

