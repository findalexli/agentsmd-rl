"""Behavioral checks for antigravity-awesome-skills-feat-add-cryptobdagent-autonomous (markdown_authoring task).

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
    text = _read('skills/crypto-bd-agent/SKILL.md')
    assert '| Wallet Forensics | Deployer analysis, fund flow | Helius (Solana), Allium (multi-chain) |' in text, "expected to find: " + '| Wallet Forensics | Deployer analysis, fund flow | Helius (Solana), Allium (multi-chain) |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/crypto-bd-agent/SKILL.md')
    assert '| On-Chain Identity | Agent registration, trust signals | ATV Web3 Identity, ERC-8004 |' in text, "expected to find: " + '| On-Chain Identity | Agent registration, trust signals | ATV Web3 Identity, ERC-8004 |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/crypto-bd-agent/SKILL.md')
    assert '| DEX Data | Prices, liquidity, pairs, chain coverage | DexScreener, GeckoTerminal |' in text, "expected to find: " + '| DEX Data | Prices, liquidity, pairs, chain coverage | DexScreener, GeckoTerminal |'[:80]

