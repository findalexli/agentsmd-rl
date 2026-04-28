"""Behavioral checks for vortex-fix-agentsmd-sccache (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vortex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- If `gh` commands fail with `error connecting to api.github.com` in sandbox, immediately rerun with' in text, "expected to find: " + '- If `gh` commands fail with `error connecting to api.github.com` in sandbox, immediately rerun with'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `cargo +nightly fmt --all` to format Rust source files. Please do this every time you reach a' in text, "expected to find: " + '- Run `cargo +nightly fmt --all` to format Rust source files. Please do this every time you reach a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Run `./scripts/public-api.sh` to re-generate the public API lock files. Please do this every time' in text, "expected to find: " + '- Run `./scripts/public-api.sh` to re-generate the public API lock files. Please do this every time'[:80]

