"""Behavioral checks for lodestar-docs-improve-agentsmd-with-architecture (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lodestar")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. Reference the [Beacon APIs spec](https://github.com/ethereum/beacon-APIs) for the endpoint contract' in text, "expected to find: " + '5. Reference the [Beacon APIs spec](https://github.com/ethereum/beacon-APIs) for the endpoint contract'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. Implement the server handler in `packages/beacon-node/src/api/impl/beacon/<resource>.ts`' in text, "expected to find: " + '3. Implement the server handler in `packages/beacon-node/src/api/impl/beacon/<resource>.ts`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Respond to review feedback promptly — reply to every comment, including bot reviewers' in text, "expected to find: " + '- Respond to review feedback promptly — reply to every comment, including bot reviewers'[:80]

