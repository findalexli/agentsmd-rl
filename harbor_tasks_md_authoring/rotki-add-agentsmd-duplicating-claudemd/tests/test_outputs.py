"""Behavioral checks for rotki-add-agentsmd-duplicating-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rotki")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- For Etherscan use the api key from ETHERSCAN_API_KEY env variable and use etherscan v2. It's as v1 but using https://api.etherscan.io/v2/api?chainid=${chainid} . As described here: https://docs.ethe" in text, "expected to find: " + "- For Etherscan use the api key from ETHERSCAN_API_KEY env variable and use etherscan v2. It's as v1 but using https://api.etherscan.io/v2/api?chainid=${chainid} . As described here: https://docs.ethe"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each combination of event type and subtype and counterparty creates a new unique event type. This is important as they are all treated differently in many parts of rotki, including the accounting. But' in text, "expected to find: " + 'Each combination of event type and subtype and counterparty creates a new unique event type. This is important as they are all treated differently in many parts of rotki, including the accounting. But'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file provides guidance for AI coding assistants (e.g., OpenAI Codex CLI, Claude Code, GitHub Copilot Chat) working with code in this repository. It mirrors the content of `CLAUDE.md` with model‑n' in text, "expected to find: " + 'This file provides guidance for AI coding assistants (e.g., OpenAI Codex CLI, Claude Code, GitHub Copilot Chat) working with code in this repository. It mirrors the content of `CLAUDE.md` with model‑n'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `string_to_evm_address()` is just a no-op typing function. It will not checksum the literal argument to a checksummed evm address. That means you should make sure to only give checksummed EVM addres' in text, "expected to find: " + '- `string_to_evm_address()` is just a no-op typing function. It will not checksum the literal argument to a checksummed evm address. That means you should make sure to only give checksummed EVM addres'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file provides guidance for AI coding assistants (e.g., OpenAI Codex CLI, Claude Code, GitHub Copilot Chat) working with code in this repository.' in text, "expected to find: " + 'This file provides guidance for AI coding assistants (e.g., OpenAI Codex CLI, Claude Code, GitHub Copilot Chat) working with code in this repository.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Component tests should follow existing patterns in `frontend/app/tests/` and `*.spec.ts`' in text, "expected to find: " + '- Component tests should follow existing patterns in `frontend/app/tests/` and `*.spec.ts`'[:80]

