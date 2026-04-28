"""Behavioral checks for opik-opik3805-docs-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opik")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Frontend: `apps/opik-frontend/.cursor/rules/` (`tech-stack.mdc`, `code-quality.mdc`, `unit-testing.mdc`, `responsive-design.mdc`).' in text, "expected to find: " + '- Frontend: `apps/opik-frontend/.cursor/rules/` (`tech-stack.mdc`, `code-quality.mdc`, `unit-testing.mdc`, `responsive-design.mdc`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/frontend_rules.mdc')
    assert 'When building components, always follow the established patterns and refer to the detailed rules for comprehensive guidelines.' in text, "expected to find: " + 'When building components, always follow the established patterns and refer to the detailed rules for comprehensive guidelines.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/frontend_rules.mdc')
    assert '10. **[Responsive Design](mdc:.cursor/rules/responsive-design.mdc)** - Tailwind CSS breakpoints vs useIsPhone hook' in text, "expected to find: " + '10. **[Responsive Design](mdc:.cursor/rules/responsive-design.mdc)** - Tailwind CSS breakpoints vs useIsPhone hook'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/responsive-design.mdc')
    assert "**Do NOT proactively add phone support** to features unless the ticket explicitly requires it. Most Opik features are desktop-first and don't need mobile optimization." in text, "expected to find: " + "**Do NOT proactively add phone support** to features unless the ticket explicitly requires it. Most Opik features are desktop-first and don't need mobile optimization."[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/responsive-design.mdc')
    assert 'This document provides clear guidelines on when to use **Tailwind CSS breakpoints** vs the **`useIsPhone` JavaScript hook** for responsive design.' in text, "expected to find: " + 'This document provides clear guidelines on when to use **Tailwind CSS breakpoints** vs the **`useIsPhone` JavaScript hook** for responsive design.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/opik-frontend/.cursor/rules/responsive-design.mdc')
    assert '3. **Working on onboarding features** - When adding or modifying onboarding components, ensure mobile support by default for new user discovery' in text, "expected to find: " + '3. **Working on onboarding features** - When adding or modifying onboarding components, ensure mobile support by default for new user discovery'[:80]

