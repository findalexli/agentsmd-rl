"""Behavioral checks for core-chore-cursor-rules-crate-guidance (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '| `relayer` | `mero-relayer` | `crates/relayer/src/main.rs` | Blockchain relay - forwards requests to NEAR/ETH/ICP/Starknet |' in text, "expected to find: " + '| `relayer` | `mero-relayer` | `crates/relayer/src/main.rs` | Blockchain relay - forwards requests to NEAR/ETH/ICP/Starknet |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '| `calimero-storage` | `crates/storage/src/lib.rs` | CRDT collections (Counter, LwwRegister, UnorderedMap, Vector) |' in text, "expected to find: " + '| `calimero-storage` | `crates/storage/src/lib.rs` | CRDT collections (Counter, LwwRegister, UnorderedMap, Vector) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '| `merod` | `merod` | `crates/merod/src/main.rs` | Node daemon - orchestrates WASM apps, storage, networking, RPC |' in text, "expected to find: " + '| `merod` | `merod` | `crates/merod/src/main.rs` | Node daemon - orchestrates WASM apps, storage, networking, RPC |'[:80]

