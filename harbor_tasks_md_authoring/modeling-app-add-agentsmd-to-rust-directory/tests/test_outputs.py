"""Behavioral checks for modeling-app-add-agentsmd-to-rust-directory (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/modeling-app")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert '- Provide doc comments on the KCL function with at least one example. When adding new examples in the KCL docs, you must register them in `example_tests.rs` under `const TEST_NAMES`.' in text, "expected to find: " + '- Provide doc comments on the KCL function with at least one example. When adding new examples in the KCL docs, you must register them in `example_tests.rs` under `const TEST_NAMES`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert '- Create a new sim test: `just new-sim-test foo_bar` (this creates a directory for your sim test like `kcl-lib/tests/foo/`, with an empty `input.kcl` that you should put code in).' in text, "expected to find: " + '- Create a new sim test: `just new-sim-test foo_bar` (this creates a directory for your sim test like `kcl-lib/tests/foo/`, with an empty `input.kcl` that you should put code in).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rust/AGENTS.md')
    assert "- Follow clippy lints: `just lint`. If the git stage is clean (i.e. there aren't any unstaged changes), you can run `just lint-fix` to automatically apply most lints." in text, "expected to find: " + "- Follow clippy lints: `just lint`. If the git stage is clean (i.e. there aren't any unstaged changes), you can run `just lint-fix` to automatically apply most lints."[:80]

