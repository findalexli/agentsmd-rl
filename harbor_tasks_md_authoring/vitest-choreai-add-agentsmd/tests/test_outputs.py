"""Behavioral checks for vitest-choreai-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitest")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces.' in text, "expected to find: " + 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This file provides guidance to Copilot Agent when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Copilot Agent when working with code in this repository.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Agent-specific guide: See [AGENTS.md](../AGENTS.md)' in text, "expected to find: " + '- Agent-specific guide: See [AGENTS.md](../AGENTS.md)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces with the following key characteristics:' in text, "expected to find: " + 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces with the following key characteristics:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **`runInlineTests`** from `test/test-utils/index.ts` - You must use this for complex file system setups (>1 file)' in text, "expected to find: " + '- **`runInlineTests`** from `test/test-utils/index.ts` - You must use this for complex file system setups (>1 file)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use utilities from `@vitest/utils/*` when available. Never import from `@vitest/utils` main entry point directly.' in text, "expected to find: " + '- Use utilities from `@vitest/utils/*` when available. Never import from `@vitest/utils` main entry point directly.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces.' in text, "expected to find: " + 'Vitest is a next-generation testing framework powered by Vite. This is a monorepo using pnpm workspaces.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.' in text, "expected to find: " + 'This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Agent-specific guide: See [AGENTS.md](AGENTS.md)' in text, "expected to find: " + '- Agent-specific guide: See [AGENTS.md](AGENTS.md)'[:80]

