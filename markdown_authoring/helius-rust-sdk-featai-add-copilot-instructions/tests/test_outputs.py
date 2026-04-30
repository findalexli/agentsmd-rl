"""Behavioral checks for helius-rust-sdk-featai-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/helius-rust-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Rust SDK for Helius APIs and Solana development. Built on `solana-client` and `tokio`, with async-first design and modular architecture. For full contributor details see [CLAUDE.md](../CLAUDE.md) and ' in text, "expected to find: " + 'Rust SDK for Helius APIs and Solana development. Built on `solana-client` and `tokio`, with async-first design and modular architecture. For full contributor details see [CLAUDE.md](../CLAUDE.md) and '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'All errors flow through the `HeliusError` enum defined in `src/error.rs`. Use `thiserror` derives and `#[from]` for conversions. Never panic — always propagate errors with `?`:' in text, "expected to find: " + 'All errors flow through the `HeliusError` enum defined in `src/error.rs`. Use `thiserror` derives and `#[from]` for conversions. Never panic — always propagate errors with `?`:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Types** — Add request/response structs in `src/types/inner.rs` (or the appropriate types file) with serde derives and `camelCase` renaming' in text, "expected to find: " + '1. **Types** — Add request/response structs in `src/types/inner.rs` (or the appropriate types file) with serde derives and `camelCase` renaming'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '// In SDK source code (src/)' in text, "expected to find: " + '// In SDK source code (src/)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'use crate::error::Result;' in text, "expected to find: " + 'use crate::error::Result;'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '// In examples and tests' in text, "expected to find: " + '// In examples and tests'[:80]

