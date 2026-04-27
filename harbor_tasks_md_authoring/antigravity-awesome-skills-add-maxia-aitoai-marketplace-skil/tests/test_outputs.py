"""Behavioral checks for antigravity-awesome-skills-add-maxia-aitoai-marketplace-skil (markdown_authoring task).

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
    text = _read('skills/maxia/SKILL.md')
    assert 'Tools: maxia_discover, maxia_register, maxia_sell, maxia_execute, maxia_negotiate, maxia_sentiment, maxia_defi_yield, maxia_token_risk, maxia_wallet_analysis, maxia_trending, maxia_fear_greed, maxia_p' in text, "expected to find: " + 'Tools: maxia_discover, maxia_register, maxia_sell, maxia_execute, maxia_negotiate, maxia_sentiment, maxia_defi_yield, maxia_token_risk, maxia_wallet_analysis, maxia_trending, maxia_fear_greed, maxia_p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/maxia/SKILL.md')
    assert 'description: Connect to MAXIA AI-to-AI marketplace on Solana. Discover, buy, sell AI services. Earn USDC. 13 MCP tools, A2A protocol, DeFi yields, sentiment analysis, rug detection.' in text, "expected to find: " + 'description: Connect to MAXIA AI-to-AI marketplace on Solana. Discover, buy, sell AI services. Earn USDC. 13 MCP tools, A2A protocol, DeFi yields, sentiment analysis, rug detection.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/maxia/SKILL.md')
    assert '-d \'{"service_id":"abc-123","prompt":"Analyze BTC sentiment","payment_tx":"optional_solana_tx_signature"}' in text, "expected to find: " + '-d \'{"service_id":"abc-123","prompt":"Analyze BTC sentiment","payment_tx":"optional_solana_tx_signature"}'[:80]

