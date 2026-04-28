"""Behavioral checks for openui-cursor-rules-changes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openui")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-rule.mdc')
    assert 'Crayon UI uses a comprehensive design system with SCSS utilities, CSS custom properties, and consistent component patterns. All styling must follow these guidelines to maintain design consistency and ' in text, "expected to find: " + 'Crayon UI uses a comprehensive design system with SCSS utilities, CSS custom properties, and consistent component patterns. All styling must follow these guidelines to maintain design consistency and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-rule.mdc')
    assert 'Prefer composition over complex variants. Create small, focused components that can be combined:' in text, "expected to find: " + 'Prefer composition over complex variants. Create small, focused components that can be combined:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/styling-rule.mdc')
    assert 'description: Comprehensive SCSS styling guidelines for the Crayon React UI component library' in text, "expected to find: " + 'description: Comprehensive SCSS styling guidelines for the Crayon React UI component library'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/use-pnpm.mdc')
    assert 'Crayon uses **pnpm** as its package manager instead of npm. pnpm provides better performance, disk efficiency, and strict dependency management. This document covers all pnpm usage patterns for the Cr' in text, "expected to find: " + 'Crayon uses **pnpm** as its package manager instead of npm. pnpm provides better performance, disk efficiency, and strict dependency management. This document covers all pnpm usage patterns for the Cr'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/use-pnpm.mdc')
    assert 'Remember: **Always use pnpm, never npm or yarn** for any package management tasks in this project.' in text, "expected to find: " + 'Remember: **Always use pnpm, never npm or yarn** for any package management tasks in this project.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/use-pnpm.mdc')
    assert 'Crayon uses pnpm workspaces for its monorepo structure. Here are the key workspace commands:' in text, "expected to find: " + 'Crayon uses pnpm workspaces for its monorepo structure. Here are the key workspace commands:'[:80]

