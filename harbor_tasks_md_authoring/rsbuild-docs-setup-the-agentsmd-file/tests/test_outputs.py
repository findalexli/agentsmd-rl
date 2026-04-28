"""Behavioral checks for rsbuild-docs-setup-the-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rsbuild")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.' in text, "expected to find: " + 'This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'pnpm lint                     # Lint code - REQUIRED before finishing' in text, "expected to find: " + 'pnpm lint                     # Lint code - REQUIRED before finishing'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'pnpm test                     # Unit tests' in text, "expected to find: " + 'pnpm test                     # Unit tests'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.' in text, "expected to find: " + 'This monorepo contains the Rsbuild build tool, plugins, and related packages. Rsbuild is a high-performance JavaScript build tool powered by Rspack.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Single test**: `pnpm test packages/core/src/foo.test.ts` (unit test) | `pnpm e2e:rspack cli/base/index.test.ts` (E2E test)' in text, "expected to find: " + '- **Single test**: `pnpm test packages/core/src/foo.test.ts` (unit test) | `pnpm e2e:rspack cli/base/index.test.ts` (E2E test)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Test**: `pnpm test` (unit tests) | `pnpm test:watch` (watch mode) | `pnpm e2e` (E2E tests)' in text, "expected to find: " + '- **Test**: `pnpm test` (unit tests) | `pnpm test:watch` (watch mode) | `pnpm e2e` (E2E tests)'[:80]

