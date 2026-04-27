"""Behavioral checks for antigravity-awesome-skills-feat-add-emblemai-crypto-wallet (markdown_authoring task).

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
    text = _read('skills/emblemai-crypto-wallet/SKILL.md')
    assert 'description: "Crypto wallet management across 7 blockchains via EmblemAI Agent Hustle API. Balance checks, token swaps, portfolio analysis, and transaction execution for Solana, Ethereum, Base, BSC, P' in text, "expected to find: " + 'description: "Crypto wallet management across 7 blockchains via EmblemAI Agent Hustle API. Balance checks, token swaps, portfolio analysis, and transaction execution for Solana, Ethereum, Base, BSC, P'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/emblemai-crypto-wallet/SKILL.md')
    assert 'You manage crypto wallets through the EmblemAI Agent Hustle API. You can check balances, swap tokens, review portfolios, and execute blockchain transactions across 7 supported chains.' in text, "expected to find: " + 'You manage crypto wallets through the EmblemAI Agent Hustle API. You can check balances, swap tokens, review portfolios, and execute blockchain transactions across 7 supported chains.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/emblemai-crypto-wallet/SKILL.md')
    assert '- [Full skill with references](https://github.com/EmblemCompany/Agent-skills/tree/main/skills/emblem-ai-agent-wallet)' in text, "expected to find: " + '- [Full skill with references](https://github.com/EmblemCompany/Agent-skills/tree/main/skills/emblem-ai-agent-wallet)'[:80]

