"""Behavioral checks for rattler-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rattler")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '../AGENTS.md' in text, "expected to find: " + '../AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Rust monorepo for conda package management (solving, installing, fetching repodata), used by pixi, rattler-build, prefix.dev' in text, "expected to find: " + '- Rust monorepo for conda package management (solving, installing, fetching repodata), used by pixi, rattler-build, prefix.dev'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Before committing, run `pixi run cargo-fmt` and `pixi run cargo-clippy` to ensure formatting and lint compliance' in text, "expected to find: " + '- Before committing, run `pixi run cargo-fmt` and `pixi run cargo-clippy` to ensure formatting and lint compliance'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- crates in `crates/`, Python bindings in `py-rattler/`, WASM bindings in `js-rattler/`' in text, "expected to find: " + '- crates in `crates/`, Python bindings in `py-rattler/`, WASM bindings in `js-rattler/`'[:80]

