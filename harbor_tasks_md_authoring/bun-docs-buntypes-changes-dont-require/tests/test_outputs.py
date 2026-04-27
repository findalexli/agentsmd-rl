"""Behavioral checks for bun-docs-buntypes-changes-dont-require (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/bun")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Edits to **TypeScript type declarations** (`packages/bun-types/**/*.d.ts`) do not touch any compiled code, so `bun bd` is unnecessary. The types test just packs the `.d.ts` files and runs `tsc` agains' in text, "expected to find: " + 'Edits to **TypeScript type declarations** (`packages/bun-types/**/*.d.ts`) do not touch any compiled code, so `bun bd` is unnecessary. The types test just packs the `.d.ts` files and runs `tsc` agains'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is an explicit exception to the "never use `bun test` directly" rule. There are no native changes for a debug build to pick up, so don\'t wait on one.' in text, "expected to find: " + 'This is an explicit exception to the "never use `bun test` directly" rule. There are no native changes for a debug build to pick up, so don\'t wait on one.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'bun test test/integration/bun-types/bun-types.test.ts' in text, "expected to find: " + 'bun test test/integration/bun-types/bun-types.test.ts'[:80]

