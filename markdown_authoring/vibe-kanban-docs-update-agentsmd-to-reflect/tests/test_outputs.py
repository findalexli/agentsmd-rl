"""Behavioral checks for vibe-kanban-docs-update-agentsmd-to-reflect (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vibe-kanban")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `git` (Git operations), `api-types` (shared API types for local + remote), ' in text, "expected to find: " + '- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `git` (Git operations), `api-types` (shared API types for local + remote), '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `shared/`: Generated TypeScript types (`shared/types.ts`, `shared/remote-types.ts`) and agent tool schemas (`shared/schemas/`). Do not edit generated files directly.' in text, "expected to find: " + '- `shared/`: Generated TypeScript types (`shared/types.ts`, `shared/remote-types.ts`) and agent tool schemas (`shared/schemas/`). Do not edit generated files directly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Do not manually edit shared/remote-types.ts, instead edit crates/remote/src/bin/remote-generate-types.rs (see crates/remote/AGENTS.md for details).' in text, "expected to find: " + 'Do not manually edit shared/remote-types.ts, instead edit crates/remote/src/bin/remote-generate-types.rs (see crates/remote/AGENTS.md for details).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('frontend/AGENTS.md')
    assert 'frontend/AGENTS.md' in text, "expected to find: " + 'frontend/AGENTS.md'[:80]

