"""Behavioral checks for astro-fix-test-commands-in-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/astro")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For focused Astro package runs: `pnpm -C packages/astro test:unit`, `pnpm -C packages/astro test:integration`, `pnpm -C packages/astro test:cli`, `pnpm -C packages/astro test:types`.' in text, "expected to find: " + '- For focused Astro package runs: `pnpm -C packages/astro test:unit`, `pnpm -C packages/astro test:integration`, `pnpm -C packages/astro test:cli`, `pnpm -C packages/astro test:types`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `pnpm -C <package-directory> test` to run a package’s tests (example: `pnpm -C packages/astro test`, `pnpm -C packages/integrations/react test`).' in text, "expected to find: " + '- Run `pnpm -C <package-directory> test` to run a package’s tests (example: `pnpm -C packages/astro test`, `pnpm -C packages/integrations/react test`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- For matching a subset by test name in Astro: `pnpm -C packages/astro test:match -- "<pattern>"`.' in text, "expected to find: " + '- For matching a subset by test name in Astro: `pnpm -C packages/astro test:match -- "<pattern>"`.'[:80]

