"""Behavioral checks for stellar-cli-add-sorobantest-integration-testing-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stellar-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Test soroban-test integration tests: `cargo test --features it --test it -- integration` -- tests the commands of the cli and is where the bulk of the tests live for this repository. All new command' in text, "expected to find: " + '- Test soroban-test integration tests: `cargo test --features it --test it -- integration` -- tests the commands of the cli and is where the bulk of the tests live for this repository. All new command'[:80]

