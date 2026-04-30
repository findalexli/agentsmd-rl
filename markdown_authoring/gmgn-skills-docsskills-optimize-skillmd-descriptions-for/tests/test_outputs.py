"""Behavioral checks for gmgn-skills-docsskills-optimize-skillmd-descriptions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gmgn-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-cooking/SKILL.md')
    assert 'description: "[FINANCIAL EXECUTION] Launch new tokens on crypto launchpads (Pump.fun, PancakeSwap, FourMeme, Bonk, BAGS, Flap, etc.) or query token creation stats via GMGN API. Requires explicit user ' in text, "expected to find: " + 'description: "[FINANCIAL EXECUTION] Launch new tokens on crypto launchpads (Pump.fun, PancakeSwap, FourMeme, Bonk, BAGS, Flap, etc.) or query token creation stats via GMGN API. Requires explicit user '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-market/SKILL.md')
    assert 'description: Get token price charts (K-line, candlestick, OHLCV), trending token rankings, and newly launched tokens on launchpads (pump.fun, letsbonk, etc.) via GMGN API. Use when user asks for token' in text, "expected to find: " + 'description: Get token price charts (K-line, candlestick, OHLCV), trending token rankings, and newly launched tokens on launchpads (pump.fun, letsbonk, etc.) via GMGN API. Use when user asks for token'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-portfolio/SKILL.md')
    assert 'description: Get wallet holdings, realized/unrealized P&L, win rate, trading history, and performance stats for any crypto wallet via GMGN API. Use when user asks for wallet holdings, wallet P&L, trad' in text, "expected to find: " + 'description: Get wallet holdings, realized/unrealized P&L, win rate, trading history, and performance stats for any crypto wallet via GMGN API. Use when user asks for wallet holdings, wallet P&L, trad'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-swap/SKILL.md')
    assert 'description: "[FINANCIAL EXECUTION] Execute on-chain token swaps and manage limit orders (stop loss, take profit) via GMGN API. Requires explicit user confirmation — executes irreversible blockchain t' in text, "expected to find: " + 'description: "[FINANCIAL EXECUTION] Execute on-chain token swaps and manage limit orders (stop loss, take profit) via GMGN API. Requires explicit user confirmation — executes irreversible blockchain t'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-token/SKILL.md')
    assert 'description: Get real-time token price, market cap, holder list, trader list, top Smart Money traders, security audit (honeypot, rug pull risk, renounced status), liquidity pool info, and social links' in text, "expected to find: " + 'description: Get real-time token price, market cap, holder list, trader list, top Smart Money traders, security audit (honeypot, rug pull risk, renounced status), liquidity pool info, and social links'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-token/SKILL.md')
    assert '| `token info` | Basic info + realtime price, liquidity, market cap, total supply, holder count, social links (market cap = price × circulating_supply) |' in text, "expected to find: " + '| `token info` | Basic info + realtime price, liquidity, market cap, total supply, holder count, social links (market cap = price × circulating_supply) |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmgn-track/SKILL.md')
    assert 'description: Get real-time trade activity from Smart Money wallets, KOL influencer wallets, and personally followed wallets via GMGN API. Use when user asks what smart money is buying, KOL trades, wha' in text, "expected to find: " + 'description: Get real-time trade activity from Smart Money wallets, KOL influencer wallets, and personally followed wallets via GMGN API. Use when user asks what smart money is buying, KOL trades, wha'[:80]

