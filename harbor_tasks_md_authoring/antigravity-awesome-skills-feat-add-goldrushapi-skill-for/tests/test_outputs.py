"""Behavioral checks for antigravity-awesome-skills-feat-add-goldrushapi-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/goldrush-api/SKILL.md')
    assert 'GoldRush by Covalent provides blockchain data across 100+ chains through a unified REST API, real-time WebSocket streams, a CLI, and an x402 pay-per-request proxy. This skill enables AI agents to quer' in text, "expected to find: " + 'GoldRush by Covalent provides blockchain data across 100+ chains through a unified REST API, real-time WebSocket streams, a CLI, and an x402 pay-per-request proxy. This skill enables AI agents to quer'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/goldrush-api/SKILL.md')
    assert 'curl -H "Authorization: Bearer $GOLDRUSH_API_KEY"   "https://api.covalenthq.com/v1/pricing/historical_by_addresses_v2/eth-mainnet/USD/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/"' in text, "expected to find: " + 'curl -H "Authorization: Bearer $GOLDRUSH_API_KEY"   "https://api.covalenthq.com/v1/pricing/historical_by_addresses_v2/eth-mainnet/USD/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/goldrush-api/SKILL.md')
    assert 'description: "Query blockchain data across 100+ chains: wallet balances, token prices, transactions, DEX pairs, and real-time OHLCV streams via the GoldRush API by Covalent."' in text, "expected to find: " + 'description: "Query blockchain data across 100+ chains: wallet balances, token prices, transactions, DEX pairs, and real-time OHLCV streams via the GoldRush API by Covalent."'[:80]

