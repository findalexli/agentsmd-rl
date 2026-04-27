"""Behavioral checks for sanity-docsagents-add-guidance-for-running (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sanity")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Important:** Do NOT use `pnpm test -- path/to/file.test.ts` for running a single file — it runs all tests across all projects. Use `pnpm vitest run --project=<project> <path>` instead.' in text, "expected to find: " + '**Important:** Do NOT use `pnpm test -- path/to/file.test.ts` for running a single file — it runs all tests across all projects. Use `pnpm vitest run --project=<project> <path>` instead.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'pnpm vitest run --project=sanity --reporter=verbose packages/sanity/src/core/hooks/useClient.test.ts' in text, "expected to find: " + 'pnpm vitest run --project=sanity --reporter=verbose packages/sanity/src/core/hooks/useClient.test.ts'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '# Run a single test file (IMPORTANT: use vitest directly with --project to avoid running all tests)' in text, "expected to find: " + '# Run a single test file (IMPORTANT: use vitest directly with --project to avoid running all tests)'[:80]

