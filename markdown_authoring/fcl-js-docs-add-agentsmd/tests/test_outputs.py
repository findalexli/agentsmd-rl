"""Behavioral checks for fcl-js-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fcl-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `npm run demo` — runs emulator + dev-wallet + Vite in `packages/demo` (requires `flow` CLI).' in text, "expected to find: " + '- `npm run demo` — runs emulator + dev-wallet + Vite in `packages/demo` (requires `flow` CLI).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `make ci` → `clean install build`, then `npm run test -- --ci` and `npm run prettier:check`.' in text, "expected to find: " + '- `make ci` → `clean install build`, then `npm run test -- --ci` and `npm run prettier:check`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Per-package scripts are uniform (see `packages/fcl/package.json`, `packages/sdk/package.json`,' in text, "expected to find: " + 'Per-package scripts are uniform (see `packages/fcl/package.json`, `packages/sdk/package.json`,'[:80]

