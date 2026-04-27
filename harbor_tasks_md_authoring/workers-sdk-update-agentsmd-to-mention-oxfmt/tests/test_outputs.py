"""Behavioral checks for workers-sdk-update-agentsmd-to-mention-oxfmt (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/workers-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Format with oxfmt - run `pnpm prettify` in the workspace root before committing' in text, "expected to find: " + '- Format with oxfmt - run `pnpm prettify` in the workspace root before committing'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `sortPackageJson` option sorts package.json keys' in text, "expected to find: " + '- `sortPackageJson` option sorts package.json keys'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Formatting (oxfmt):**' in text, "expected to find: " + '**Formatting (oxfmt):**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/create-cloudflare/AGENTS.md')
    assert 'packages/create-cloudflare/AGENTS.md' in text, "expected to find: " + 'packages/create-cloudflare/AGENTS.md'[:80]

