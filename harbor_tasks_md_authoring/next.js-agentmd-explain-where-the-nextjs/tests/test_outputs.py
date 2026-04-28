"""Behavioral checks for next.js-agentmd-explain-where-the-nextjs (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/next.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The main Next.js framework lives in `packages/next/`. This is what gets published as the `next` npm package.' in text, "expected to find: " + 'The main Next.js framework lives in `packages/next/`. This is what gets published as the `next` npm package.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a pnpm monorepo containing the Next.js framework and related packages.' in text, "expected to find: " + 'This is a pnpm monorepo containing the Next.js framework and related packages.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'See [Codebase structure](#codebase-structure) above for detailed explanations.' in text, "expected to find: " + 'See [Codebase structure](#codebase-structure) above for detailed explanations.'[:80]

