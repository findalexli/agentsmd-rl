"""Behavioral checks for mastra-chore-add-cursor-rules-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mastra")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/.cursor/rules/frontend.mdc')
    assert '`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.' in text, "expected to find: " + '`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/.cursor/rules/frontend.mdc')
    assert '- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested' in text, "expected to find: " + '- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/.cursor/rules/frontend.mdc')
    assert 'Standards and conventions for building components in `packages/playground-ui`.' in text, "expected to find: " + 'Standards and conventions for building components in `packages/playground-ui`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/CLAUDE.md')
    assert '`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.' in text, "expected to find: " + '`packages/playground-ui` provides shared UI and business logic primitives for multiple studio environments.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/CLAUDE.md')
    assert '- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested' in text, "expected to find: " + '- **FORBIDDEN**: Arbitrary values (e.g., `bg-[#1A1A1A]`) unless explicitly requested'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground-ui/CLAUDE.md')
    assert 'Standards and conventions for building components in `packages/playground-ui`.' in text, "expected to find: " + 'Standards and conventions for building components in `packages/playground-ui`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/.cursor/rules/frontend.mdc')
    assert '`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.' in text, "expected to find: " + '`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/.cursor/rules/frontend.mdc')
    assert 'This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.' in text, "expected to find: " + 'This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/.cursor/rules/frontend.mdc')
    assert 'Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.' in text, "expected to find: " + 'Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/CLAUDE.md')
    assert '`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.' in text, "expected to find: " + '`packages/playground` is a local development studio built with React Router that composes primitives from `packages/playground-ui`.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/CLAUDE.md')
    assert 'This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.' in text, "expected to find: " + 'This package is a **thin composition layer** only. All reusable logic must live in `packages/playground-ui`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/playground/CLAUDE.md')
    assert 'Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.' in text, "expected to find: " + 'Pages should compose high-level components from `packages/playground-ui` with minimal custom logic.'[:80]

