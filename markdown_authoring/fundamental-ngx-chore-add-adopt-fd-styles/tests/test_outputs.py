"""Behavioral checks for fundamental-ngx-chore-add-adopt-fd-styles (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fundamental-ngx")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adopt-styles/SKILL.md')
    assert 'find <matched-directory> \\( -name "*.component.ts" -o -name "*.component.html" -o -name "*.component.spec.ts" -o -name "*.directive.ts" -o -name "*.directive.html" -o -name "*.directive.spec.ts" \\)' in text, "expected to find: " + 'find <matched-directory> \\( -name "*.component.ts" -o -name "*.component.html" -o -name "*.component.spec.ts" -o -name "*.directive.ts" -o -name "*.directive.html" -o -name "*.directive.spec.ts" \\)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adopt-styles/SKILL.md')
    assert 'This catches issues like string-attribute vs property-binding mismatches (e.g., `tabindex="0"` vs `[tabindex]="0"`) before investing time in test creation. Fix any build errors before proceeding.' in text, "expected to find: " + 'This catches issues like string-attribute vs property-binding mismatches (e.g., `tabindex="0"` vs `[tabindex]="0"`) before investing time in test creation. Fix any build errors before proceeding.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adopt-styles/SKILL.md')
    assert '| Category                        | What to look for                                                                                                                                    |' in text, "expected to find: " + '| Category                        | What to look for                                                                                                                                    |'[:80]

