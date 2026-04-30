"""Behavioral checks for antigravity-awesome-skills-add-raydencode-and-raydenuse-skil (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-code/SKILL.md')
    assert 'Generate production-quality React + Tailwind CSS code using the Rayden UI component library (34 components). The skill loads a complete API reference with every component, every prop, design tokens, l' in text, "expected to find: " + 'Generate production-quality React + Tailwind CSS code using the Rayden UI component library (34 components). The skill loads a complete API reference with every component, every prop, design tokens, l'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-code/SKILL.md')
    assert "**Use case:** You're building an internal analytics tool and need a full dashboard page with MetricsCard grid, sortable Table, and ActivityFeed sidebar — all with correct Rayden imports and token clas" in text, "expected to find: " + "**Use case:** You're building an internal analytics tool and need a full dashboard page with MetricsCard grid, sortable Table, and ActivityFeed sidebar — all with correct Rayden imports and token clas"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-code/SKILL.md')
    assert "**Use case:** You're building a storefront and need a responsive product grid with Chip filters, Input search, Pagination, and Cards with images — all using Rayden's layout and spacing rules." in text, "expected to find: " + "**Use case:** You're building a storefront and need a responsive product grid with Chip filters, Input search, Pagination, and Cards with images — all using Rayden's layout and spacing rules."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-use/SKILL.md')
    assert 'Build and maintain Rayden UI components and screens directly in Figma using the Figma MCP. The skill enforces the Rayna UI design system — resolved design tokens, craft rules, anti-pattern detection, ' in text, "expected to find: " + 'Build and maintain Rayden UI components and screens directly in Figma using the Figma MCP. The skill enforces the Rayna UI design system — resolved design tokens, craft rules, anti-pattern detection, '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-use/SKILL.md')
    assert "**Use case:** You're starting a new design system file and need the Button component with all variants (primary, secondary, grey, destructive) in solid and outlined appearances across SM and LG sizes." in text, "expected to find: " + "**Use case:** You're starting a new design system file and need the Button component with all variants (primary, secondary, grey, destructive) in solid and outlined appearances across SM and LG sizes."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/rayden-use/SKILL.md')
    assert '7. **Visual validation** — Takes screenshots after each build stage and validates against 8 acceptance criteria (alignment, spacing, color accuracy, hierarchy, radius, shadow, primary action count)' in text, "expected to find: " + '7. **Visual validation** — Takes screenshots after each build stage and validates against 8 acceptance criteria (alignment, spacing, color accuracy, hierarchy, radius, shadow, primary action count)'[:80]

