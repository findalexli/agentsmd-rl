"""Behavioral checks for baml-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/baml")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/instructions.mdc')
    assert 'You should prefer writing Rust unit tests. If you do need to run integ tests or create a new client integ test, try just running the python ones using uv + maturin to build + and pytest to test that p' in text, "expected to find: " + 'You should prefer writing Rust unit tests. If you do need to run integ tests or create a new client integ test, try just running the python ones using uv + maturin to build + and pytest to test that p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/instructions.mdc')
    assert 'If infisical CLI _is_ available, then feel free to use it as some scripts use it, otherwise, assume you have the right env vars in your environment and manually run some of the commands without the `i' in text, "expected to find: " + 'If infisical CLI _is_ available, then feel free to use it as some scripts use it, otherwise, assume you have the right env vars in your environment and manually run some of the commands without the `i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/instructions.mdc')
    assert '`cargo fmt -- --config imports_granularity="Crate" --config group_imports="StdExternalCrate"` in engine directory if you changed any Rust files there. It will solve linter issues.' in text, "expected to find: " + '`cargo fmt -- --config imports_granularity="Crate" --config group_imports="StdExternalCrate"` in engine directory if you changed any Rust files there. It will solve linter issues.'[:80]

