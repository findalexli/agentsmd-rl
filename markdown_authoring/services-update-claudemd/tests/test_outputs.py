"""Behavioral checks for services-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/services")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Memory allocator: Uses jemalloc by default with built-in heap profiling support (enable at runtime via MALLOC_CONF environment variable). Can optionally use mimalloc via `--features mimalloc-allocat' in text, "expected to find: " + '- Memory allocator: Uses jemalloc by default with built-in heap profiling support (enable at runtime via MALLOC_CONF environment variable). Can optionally use mimalloc via `--features mimalloc-allocat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Alloy (Web3 library)**: Fetch https://alloy.rs/introduction/prompting for an AI-optimized guide covering providers, transactions, contracts, and migration from ethers-rs' in text, "expected to find: " + '- **Alloy (Web3 library)**: Fetch https://alloy.rs/introduction/prompting for an AI-optimized guide covering providers, transactions, contracts, and migration from ethers-rs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Runs in **Fork** mode: anvil forks a real network via `ETH_RPC_URL` (set in `playground/.env`). A clean local network mode is planned but not yet implemented.' in text, "expected to find: " + '- Runs in **Fork** mode: anvil forks a real network via `ETH_RPC_URL` (set in `playground/.env`). A clean local network mode is planned but not yet implemented.'[:80]

