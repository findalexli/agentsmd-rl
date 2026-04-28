"""Behavioral checks for mono-chore-clean-up-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mono")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Re-exports are common: main packages re-export from sub-packages (e.g., `packages/zero/src/mod.ts` → exports from `zero-client`, `zero-server`)' in text, "expected to find: " + '- Re-exports are common: main packages re-export from sub-packages (e.g., `packages/zero/src/mod.ts` → exports from `zero-client`, `zero-server`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Prefer package-level commands when possible. Each package supports: `test`, `check-types`, `lint`, `format`, `build`. e.g.:' in text, "expected to find: " + 'Prefer package-level commands when possible. Each package supports: `test`, `check-types`, `lint`, `format`, `build`. e.g.:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Replicache**: Client-side store managed by `zero-client` and `replicache`, in IndexedDB by default' in text, "expected to find: " + '- **Replicache**: Client-side store managed by `zero-client` and `replicache`, in IndexedDB by default'[:80]

