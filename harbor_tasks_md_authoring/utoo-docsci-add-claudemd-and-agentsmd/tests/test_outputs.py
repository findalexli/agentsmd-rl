"""Behavioral checks for utoo-docsci-add-claudemd-and-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/utoo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `next.js/` directory is a **git submodule** (`utooland/next.js`) providing Turbopack crates. Many Rust crates depend on paths within it. Initialize with `git submodule update --init --recursive`.' in text, "expected to find: " + 'The `next.js/` directory is a **git submodule** (`utooland/next.js`) providing Turbopack crates. Many Rust crates depend on paths within it. Initialize with `git submodule update --init --recursive`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Bundler snapshot tests live in `crates/pack-tests/tests/snapshot/`. Each test case has an `input/` dir and an `output/` dir with expected results. Set `UPDATE=1` to regenerate snapshots.' in text, "expected to find: " + 'Bundler snapshot tests live in `crates/pack-tests/tests/snapshot/`. Each test case has an `input/` dir and an `output/` dir with expected results. Set `UPDATE=1` to regenerate snapshots.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| `pm` | Package manager CLI (`utoo`/`ut`). Modules: `cmd/` (CLI commands), `service/` (business logic), `util/` (registry, cache, linker), `helper/` (workspace, deps) |' in text, "expected to find: " + '| `pm` | Package manager CLI (`utoo`/`ut`). Modules: `cmd/` (CLI commands), `service/` (business logic), `util/` (registry, cache, linker), `helper/` (workspace, deps) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

