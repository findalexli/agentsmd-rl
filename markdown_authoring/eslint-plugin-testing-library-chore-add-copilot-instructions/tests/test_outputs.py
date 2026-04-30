"""Behavioral checks for eslint-plugin-testing-library-chore-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/eslint-plugin-testing-library")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is an ESLint plugin that enforces best practices for Testing Library (DOM, React, Vue, Angular, Svelte, Marko). The plugin provides 30 ESLint rules to catch common mistakes when writing tests wit' in text, "expected to find: " + 'This is an ESLint plugin that enforces best practices for Testing Library (DOM, React, Vue, Angular, Svelte, Marko). The plugin provides 30 ESLint rules to catch common mistakes when writing tests wit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. Enable pnpm via corepack: `corepack enable pnpm` (uses version from `package.json` `packageManager` field)' in text, "expected to find: " + '1. Enable pnpm via corepack: `corepack enable pnpm` (uses version from `package.json` `packageManager` field)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| Command                     | Purpose                  | Time | Notes                         |' in text, "expected to find: " + '| Command                     | Purpose                  | Time | Notes                         |'[:80]

