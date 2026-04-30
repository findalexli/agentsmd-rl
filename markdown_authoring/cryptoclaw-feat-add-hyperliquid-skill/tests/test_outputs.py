"""Behavioral checks for cryptoclaw-feat-add-hyperliquid-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cryptoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperliquid/SKILL.md')
    assert 'Trade perpetual futures and spot tokens on Hyperliquid — a high-performance DEX built on its own L1 chain. USDC is the primary collateral for perpetuals; the native token is HYPE.' in text, "expected to find: " + 'Trade perpetual futures and spot tokens on Hyperliquid — a high-performance DEX built on its own L1 chain. USDC is the primary collateral for perpetuals; the native token is HYPE.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperliquid/SKILL.md')
    assert '**Strongly recommended:** Use the official Python SDK (`hyperliquid-python-sdk`) or a community TypeScript SDK for signing. Manual EIP-712 construction is error-prone.' in text, "expected to find: " + '**Strongly recommended:** Use the official Python SDK (`hyperliquid-python-sdk`) or a community TypeScript SDK for signing. Manual EIP-712 construction is error-prone.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/hyperliquid/SKILL.md')
    assert 'Returns: `marginSummary` (accountValue, totalMarginUsed, withdrawable), `assetPositions` array (coin, size, entryPx, unrealizedPnl, leverage, liquidationPx).' in text, "expected to find: " + 'Returns: `marginSummary` (accountValue, totalMarginUsed, withdrawable), `assetPositions` array (coin, size, entryPx, unrealizedPnl, leverage, liquidationPx).'[:80]

