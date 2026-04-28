"""Behavioral checks for rstest-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rstest")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Core implementation lives in `packages/core/src`, with mirrored tests in `packages/core/tests` (for example, `src/core/plugins/mockLoader.mjs` ↔ `tests/core/mockLoader.test.ts`).' in text, "expected to find: " + '- Core implementation lives in `packages/core/src`, with mirrored tests in `packages/core/tests` (for example, `src/core/plugins/mockLoader.mjs` ↔ `tests/core/mockLoader.test.ts`).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `pnpm --filter @rstest/core test` executes the unit suite; add `-- tests/core/mockLoader.test.ts` for a single file and append `-- --updateSnapshot` only when behavior changes.' in text, "expected to find: " + '- `pnpm --filter @rstest/core test` executes the unit suite; add `-- tests/core/mockLoader.test.ts` for a single file and append `-- --updateSnapshot` only when behavior changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `examples/` holds usage demos, `e2e/` carries integration suites and fixtures, and `scripts/` plus `website/` supply build utilities and documentation assets.' in text, "expected to find: " + '- `examples/` holds usage demos, `e2e/` carries integration suites and fixtures, and `scripts/` plus `website/` supply build utilities and documentation assets.'[:80]

