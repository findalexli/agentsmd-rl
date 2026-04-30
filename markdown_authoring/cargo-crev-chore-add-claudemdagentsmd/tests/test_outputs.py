"""Behavioral checks for cargo-crev-chore-add-claudemdagentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cargo-crev")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'AGENTS.md' in text, "expected to find: " + 'AGENTS.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '4. **crev-lib** — Library API (like libgit2 for Crev): local proof store, identity management, git-backed repos' in text, "expected to find: " + '4. **crev-lib** — Library API (like libgit2 for Crev): local proof store, identity management, git-backed repos'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '2. **crev-data** — Core data types: proofs, identities, trust levels, cryptographic signing (ed25519-dalek)' in text, "expected to find: " + '2. **crev-data** — Core data types: proofs, identities, trust levels, cryptographic signing (ed25519-dalek)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Each layer may only depend on layers below it. The `crevette` crate is excluded from the workspace.' in text, "expected to find: " + 'Each layer may only depend on layers below it. The `crevette` crate is excluded from the workspace.'[:80]

