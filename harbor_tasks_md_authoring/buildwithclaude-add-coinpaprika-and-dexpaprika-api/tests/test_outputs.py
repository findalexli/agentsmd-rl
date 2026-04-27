"""Behavioral checks for buildwithclaude-add-coinpaprika-and-dexpaprika-api (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/coinpaprika-api/SKILL.md')
    assert 'description: "Access cryptocurrency market data from CoinPaprika: prices, tickers, OHLCV, exchanges, contract lookups for 12,000+ coins and 350+ exchanges. Free tier, no API key needed. Install MCP: a' in text, "expected to find: " + 'description: "Access cryptocurrency market data from CoinPaprika: prices, tickers, OHLCV, exchanges, contract lookups for 12,000+ coins and 350+ exchanges. Free tier, no API key needed. Install MCP: a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/coinpaprika-api/SKILL.md')
    assert '- `getPlatforms` / `getContracts` / `getTickerByContract` / `getHistoricalTickerByContract` — Contract lookups' in text, "expected to find: " + '- `getPlatforms` / `getContracts` / `getTickerByContract` / `getHistoricalTickerByContract` — Contract lookups'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/coinpaprika-api/SKILL.md')
    assert 'Access cryptocurrency market data for 12,000+ coins and 350+ exchanges via the CoinPaprika MCP server.' in text, "expected to find: " + 'Access cryptocurrency market data for 12,000+ coins and 350+ exchanges via the CoinPaprika MCP server.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/dexpaprika-api/SKILL.md')
    assert 'description: "Access DeFi data from DexPaprika: token prices, liquidity pools, OHLCV, transactions across 34+ blockchains and 30M+ pools. Free, no API key needed. Install MCP: add https://mcp.dexpapri' in text, "expected to find: " + 'description: "Access DeFi data from DexPaprika: token prices, liquidity pools, OHLCV, transactions across 34+ blockchains and 30M+ pools. Free, no API key needed. Install MCP: add https://mcp.dexpapri'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/dexpaprika-api/SKILL.md')
    assert 'Access DeFi data across 34+ blockchains, 30M+ liquidity pools, and 28M+ tokens via the DexPaprika MCP server.' in text, "expected to find: " + 'Access DeFi data across 34+ blockchains, 30M+ liquidity pools, and 28M+ tokens via the DexPaprika MCP server.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/dexpaprika-api/SKILL.md')
    assert '`ethereum`, `solana`, `bsc`, `polygon`, `arbitrum`, `base`, `avalanche`, `optimism`, `sui`, `ton`, `tron`' in text, "expected to find: " + '`ethereum`, `solana`, `bsc`, `polygon`, `arbitrum`, `base`, `avalanche`, `optimism`, `sui`, `ton`, `tron`'[:80]

