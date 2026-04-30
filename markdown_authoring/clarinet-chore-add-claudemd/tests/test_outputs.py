"""Behavioral checks for clarinet-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/clarinet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Clarinet is a development toolkit for building, testing, and deploying Clarity smart contracts on the Stacks blockchain. It provides a CLI, REPL, testing framework, debugger, and local devnet environm' in text, "expected to find: " + 'Clarinet is a development toolkit for building, testing, and deploying Clarity smart contracts on the Stacks blockchain. It provides a CLI, REPL, testing framework, debugger, and local devnet environm'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Clarity interpreter and Stacks libraries come from `stacks-network/stacks-core` git dependency (see `Cargo.toml` for current revision).' in text, "expected to find: " + 'Clarity interpreter and Stacks libraries come from `stacks-network/stacks-core` git dependency (see `Cargo.toml` for current revision).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) for commit messages' in text, "expected to find: " + '- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) for commit messages'[:80]

