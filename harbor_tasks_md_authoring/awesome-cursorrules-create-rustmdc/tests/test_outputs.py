"""Behavioral checks for awesome-cursorrules-create-rustmdc (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/rust.mdc')
    assert 'description: Rust best practices for Solana smart contract development using Anchor framework and Solana SDK' in text, "expected to find: " + 'description: Rust best practices for Solana smart contract development using Anchor framework and Solana SDK'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/rust.mdc')
    assert '- Prefer `Init`, `Close`, `Realloc`, `Mut`, and constraint macros to avoid manual deserialization' in text, "expected to find: " + '- Prefer `Init`, `Close`, `Realloc`, `Mut`, and constraint macros to avoid manual deserialization'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules-new/rust.mdc')
    assert '- Validate accounts strictly using constraint macros (e.g., `#[account(mut)]`, `seeds`, `bump]`)' in text, "expected to find: " + '- Validate accounts strictly using constraint macros (e.g., `#[account(mut)]`, `seeds`, `bump]`)'[:80]

