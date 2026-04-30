"""Behavioral checks for templewallet-extension-tw2089-agentsmd-setup (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/templewallet-extension")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository is the Temple Wallet browser extension codebase. Temple Wallet is an open-source multichain wallet for Tezos & EVM-compatible blockchains, focusing on security and seamless UX.' in text, "expected to find: " + 'This repository is the Temple Wallet browser extension codebase. Temple Wallet is an open-source multichain wallet for Tezos & EVM-compatible blockchains, focusing on security and seamless UX.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'We are building this together. When you learn something non-obvious, add it here so future changes go faster.' in text, "expected to find: " + 'We are building this together. When you learn something non-obvious, add it here so future changes go faster.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. Stay aligned with the existing architecture. Prefer small, targeted improvements over new abstractions.' in text, "expected to find: " + '3. Stay aligned with the existing architecture. Prefer small, targeted improvements over new abstractions.'[:80]

